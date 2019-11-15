
document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');

  var calendar = new Calendar(calendarEl, {
    plugins: [ 'interaction', 'dayGrid', 'timeGrid' ],
    defaultView: 'dayGridMonth',
    defaultDate: '2019-11-07',
    header: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
  });

  calendar.render();
});