from scapy.all import sniff, DNS, TCP, Raw
from datetime import datetime
from app import create_app
from app.models import Log, db

# Will be deprecated, because of Go daemon (claws_daemon.go)
def packet_callback(packet):
    try:
        # Обработка DNS
        if packet.haslayer(DNS):
            dns = packet[DNS]
            if dns.qr == 0 and dns.qd:  # DNS запрос
                log = Log(
                    timestamp=datetime.now(),
                    source_ip=packet[1].src,
                    destination_ip=packet[1].dst,
                    query_type="DNS",
                    query_data=dns.qd.qname.decode('utf-8')
                )
                db.session.add(log)
                db.session.commit()
            elif dns.qr == 1 and dns.an:  # DNS ответ
                print(f"DNS Response: {dns.an.rdata}")

        # Обработка HTTP (через TCP + Raw)
        if packet.haslayer(TCP) and packet.haslayer(Raw):
            raw_load = packet[Raw].load
            try:
                raw_load_decoded = raw_load.decode('utf-8', errors='ignore')  # Декодирование
                if "GET" in raw_load_decoded or "POST" in raw_load_decoded:
                    # Добавляем лог в базу
                    log = Log(
                        timestamp=datetime.now(),
                        source_ip=packet[1].src,
                        destination_ip=packet[1].dst,
                        query_type="HTTP",
                        query_data=raw_load_decoded
                    )

                    db.session.add(log)
                    db.session.commit()

                    # Для отладки можно оставить вывод в консоль
                    print(f"HTTP Request:\n{raw_load_decoded}")
            except UnicodeDecodeError:
                pass  # Игнорируем недекодируемые данные
    except Exception as e:
        print(f"[!] Error processing packet: {e}")


def catcher():
    app = create_app()
    with app.app_context():
        try:
            print("[*] Starting packet sniffer...")
            sniff(prn=packet_callback, filter="tcp or udp", store=False)

        except KeyboardInterrupt:
            print("\n[!] Stopping packet sniffer.")


catcher()
