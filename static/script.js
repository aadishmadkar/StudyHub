const timerElement =
document.getElementById("timer");

if(timerElement){

    const start =
    new Date(
        timerElement.dataset.start
    );

    function updateTimer(){

        const now = new Date();

        const diff =
        Math.floor(
            (now - start)/1000
        );

        const hrs =
        Math.floor(diff/3600);

        const mins =
        Math.floor(
            (diff%3600)/60
        );

        const secs =
        diff%60;

        timerElement.innerHTML =
        "⏱ " +
        String(hrs).padStart(2,'0')
        + ":" +
        String(mins).padStart(2,'0')
        + ":" +
        String(secs).padStart(2,'0');
    }

    updateTimer();

    setInterval(
        updateTimer,
        1000
    );
}