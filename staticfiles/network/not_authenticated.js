document.addEventListener('DOMContentLoaded', function() {
    // Init posts
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
