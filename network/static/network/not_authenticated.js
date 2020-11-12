document.addEventListener('DOMContentLoaded', function() {

    /* Update all:
        * like counters
        * add like amount indicator control
        * sort amojis by data-count 
    */ 
    document.querySelectorAll("div.post").forEach((postNode) => {
        updateLikeCounter(postNode);
        likesAmountIndicatorControl(postNode);
        sortEmojiList(postNode);
        showMoreButtonControl(postNode);
    })

    window.onresize = () => {
        document.querySelectorAll("div.post").forEach((postNode) => {
            showMoreButtonControl(postNode);
        })
    }
});
