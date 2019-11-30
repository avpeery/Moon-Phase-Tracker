document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');

    $.get('/get-moon-phases.json', (res) => {

        function tooltip(info) {
              var tooltip = new Tooltip(info.el, {
                title: `<a href="/add-to-calendar?title=${info.event.title}&date=${info.event.start}">Add to your calendar</a>`,
                html: true,
                placement: 'top',
                trigger: 'click',
                container: 'body'
              })
        };

        var calendar = new FullCalendar.Calendar(calendarEl, {
            header: {
                left: 'today',
                center: 'title',
                right: 'prev,next'
            },
            navLinks: true,
            plugins: [ 'dayGrid' ],
            events: res,
            displayEventTime: false,
            eventRender: tooltip
             })   

        calendar.render();

    });
});

