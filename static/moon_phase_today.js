
function load_moon_phases(obj){
    var gets=[]
    for (var i in obj){
        gets.push(i+"="+encodeURIComponent(obj[i]))
    }   
    var xmlhttp = new XMLHttpRequest()
    var url = "https://www.icalendar37.net/lunar/api/?"+gets.join("&")
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var moon  = JSON.parse(xmlhttp.responseText)
            example_1(moon)
        }
    }
    xmlhttp.open("GET", url, true)
    xmlhttp.send()
}
document.addEventListener("DOMContentLoaded", function() { 
    var configMoon = {
        lang        :'en', // 'ca' 'de' 'en' 'es' 'fr' 'it' 'pl' 'pt' 'ru' 'zh' (*)
        month       :new Date().getMonth() + 1, // 1  - 12
        year        :new Date().getFullYear(),
        size        :50, //pixels
        lightColor  :"#FFFF88", //CSS color
        shadeColor  :"#111111", //CSS color
        sizeQuarter :20, //pixels
        texturize   :false //true - false
    }
    configMoon.LDZ=new Date(configMoon.year,configMoon.month-1,1)/1000
    load_moon_phases(configMoon)
})

function example_1(moon){
    console.log(moon)
    var day = new Date().getDate()
    var dayWeek=moon.phase[day].dayWeek
    var html="<div class='moon'>"
    html+="<div>"+moon.nameDay[dayWeek]+"</div>"
    html+="<div>"+ day + " " + moon.monthName + " "+moon.year+"</div>"
    html+=moon.phase[day].svg
    html+="<div>"+moon.phase[day].phaseName + " "+ Math.round(moon.phase[day].lighting)+"%</div>"
    html+="</div>"
    document.getElementById("moonphasetoday").innerHTML=html
}
