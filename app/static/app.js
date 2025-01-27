$(document).ready(function () {
    function updateSortIcons() {
        var currentUrl = new URL(window.location.href);
        var currentSort = currentUrl.searchParams.get('sort');
        var currentOrder = currentUrl.searchParams.get('order');

        $('.sortable').each(function () {
            var sortBy = $(this).data('sort');
            if (sortBy === currentSort) {
                var icon = currentOrder === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
                $(this).append(` <i class="fas ${icon}"></i>`);
            } else {
                $(this).find('i').remove();
            }
        });
    }

    $('.sortable').click(function () {
        var sortBy = $(this).data('sort');
        var currentUrl = new URL(window.location.href);
        var currentSort = currentUrl.searchParams.get('sort');
        var currentOrder = currentUrl.searchParams.get('order');

        var newOrder = 'asc';
        if (currentSort === sortBy && currentOrder === 'asc') {
            newOrder = 'desc';
        }

        currentUrl.searchParams.set('sort', sortBy);
        currentUrl.searchParams.set('order', newOrder);
        window.location.href = currentUrl.toString();
    });

    updateSortIcons();
});