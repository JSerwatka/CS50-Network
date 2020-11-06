document.addEventListener('DOMContentLoaded', function() {

    // Update all like counters and icons 
    document.querySelectorAll("div.post").forEach((postNode) => {
        updateLikeCounter(postNode);
        likesAmountIndicatorControl(postNode);
        sortEmojiList(postNode);
    })


})
