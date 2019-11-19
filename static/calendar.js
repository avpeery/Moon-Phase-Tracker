document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    $.get('/get-moon-phases.json', (res) => {

    var calendar = new FullCalendar.Calendar(calendarEl, {
        plugins: [ 'dayGrid' ],
        events: res,
});
    calendar.render();
});

});