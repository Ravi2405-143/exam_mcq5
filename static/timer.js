document.addEventListener('DOMContentLoaded', function () {
    // DURATION is defined in global scope from exam.html template
    if (typeof DURATION !== 'undefined') {
        let totalSeconds = DURATION * 60;
        const timerEl = document.getElementById("timer");

        if (timerEl) {
            const interval = setInterval(() => {
                let minutes = Math.floor(totalSeconds / 60);
                let seconds = totalSeconds % 60;

                timerEl.innerText =
                    String(minutes).padStart(2, "0") +
                    ":" +
                    String(seconds).padStart(2, "0");

                if (totalSeconds <= 0) {
                    clearInterval(interval);
                    const form = document.getElementById("examForm");
                    if (form) form.submit();
                }

                totalSeconds--;
            }, 1000);
        }
    }
});
