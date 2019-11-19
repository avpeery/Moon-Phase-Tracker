document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    $.get('/get-moon-phases.json', (res) => {

    var calendar = new FullCalendar.Calendar(calendarEl, {
        plugins: [ 'dayGrid' ],
        events: res,
        eventClick: function(events) {
            alert('Event: ' + events.event.title);
            alert('Coordinates: ' + events.jsEvent.pageX + ',' + events.jsEvent.pageY);
            alert('View: ' + events.view.type)
        }
    });
    calendar.render();
});
});