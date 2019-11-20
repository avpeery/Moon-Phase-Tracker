document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    $.get('/get-moon-phases.json', (res) => {

        var calendar = new FullCalendar.Calendar(calendarEl, {
            plugins: [ 'dayGrid' ],
            events: res,
            displayEventTime: false,
            eventRender: function(info) {
              var tooltip = new Tooltip(info.el, {
                title: info.event.title,
                placement: 'top',
                trigger: 'hover',
                container: 'body'
              });
             },

        });
    
    calendar.render();
    });

});