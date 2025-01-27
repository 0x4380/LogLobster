package main

import (
  "database/sql"
  "fmt"
  "log"
  "net"
  "net/http"
  "time"

  "github.com/google/gopacket"
  "github.com/google/gopacket/pcap"
  _ "github.com/mattn/go-sqlite3"
)

// structure
type HttpLog struct {
  Timestamp time.Time
  Method    string
  Host      string
  Path      string
  Protocol  string
  UserAgent string
}

// Writing log to db
func logHttpRequest(db *sql.DB, log HttpLog) {
  query := `INSERT INTO http_logs (timestamp, method, host, path, protocol, user_agent) VALUES (?, ?, ?, ?, ?, ?)`
  _, err := db.Exec(query, log.Timestamp, log.Method, log.Host, log.Path, log.Protocol, log.UserAgent)
  if err != nil {
    log.Printf("Error writing log to database: %v", err)
  }
}

// HTTP server for catching HTTP requests
func httpHandler(db *sql.DB) http.Handler {
  return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    logHttpRequest(db, HttpLog{
      Timestamp: time.Now(),
      Method:    r.Method,
      Host:      r.Host,
      Path:      r.URL.Path,
      Protocol:  r.Proto,
      UserAgent: r.UserAgent(),
    })
    // simple response
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("Request logged"))
  })
}

// Processing packets
func handlePackets(pcapFile string, db *sql.DB) {
  handle, err := pcap.OpenLive(pcapFile, 1600, true, pcap.BlockForever)
  if err != nil {
    log.Fatal(err)
  }
  defer handle.Close()

  packetSource := gopacket.NewPacketSource(handle, handle.LinkType())

  for packet := range packetSource.Packets() {
    if packet.NetworkLayer() != nil {
      // Logging other protocols (f.e. ICMP, DNS)
      if packet.NetworkLayer().LayerType() == gopacket.LayerTypeIPv4 {
        // ICMP packet handle sample
        if packet.TransportLayer() != nil && packet.TransportLayer().LayerType() == gopacket.LayerTypeICMPv4 {
          log.Println("ICMP пакет пойман!")
          // Writing packet info to DB
          // Simply printing for sample
          log.Println(packet)
        }

        // DNS packet sample
        if packet.ApplicationLayer() != nil && packet.ApplicationLayer().LayerType() == gopacket.LayerTypeDNS {
          log.Println("DNS запрос пойман!")
          // Write to DB
          // Temporary, just printing it
          log.Println(packet)
        }
      }
    }
  }
}


func main() {
  // Connecting to LogLobster DB
  db, err := sql.Open("sqlite3", "./logs.db")
  if err != nil {
    log.Fatal(err)
  }
  defer db.Close()

  // Creating table
  createTable := `CREATE TABLE IF NOT EXISTS http_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME,
    method TEXT,
    host TEXT,
    path TEXT,
    protocol TEXT,
    user_agent TEXT
  );`
  _, err = db.Exec(createTable)
  if err != nil {
    log.Fatal(err)
  }

  // Launchung HTTP server
  http.Handle("/", httpHandler(db))
  go func() {
    log.Println("HTTP сервер слушает на порту 8080")
    err := http.ListenAndServe(":8080", nil)
    if err != nil {
      log.Fatal("Ошибка запуска HTTP сервера:", err)
    }
  }()

  go handlePackets("eth0", db) // Choose interface for listening

  // Hack for locking main flow
  select {}
}