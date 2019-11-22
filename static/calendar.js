document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');

    $.get('/get-moon-phases.json', (res) => {

        function tooltip(info) {
              var tooltip = new Tooltip(info.el, {
                title: `<a class="sendAuthorization" href="/authorize?title=${info.event.title}&date=${info.event.start}">Add to your calendar</a>`,
                html: true,
                placement: 'top',
                trigger: 'hover',
                container: 'body'
              })
        };

        var calendar = new FullCalendar.Calendar(calendarEl, {
            plugins: [ 'dayGrid' ],
            events: res,
            displayEventTime: false,
            eventRender: tooltip
             })   
    
        calendar.render();

    });

})



