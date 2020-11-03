document.addEventListener('DOMContentLoaded', function() {
    likesAmountIndicatorControl();
    // Update all like counters and icons 
    document.querySelectorAll("div.post").forEach((postNode) => {
        updateLikeCounter(postNode)
    })


})
