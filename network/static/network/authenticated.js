document.addEventListener('DOMContentLoaded', function() {
    editPostControl();
    likePanelAnimationControl();
    likeHandling();
    
    // Update all like counters, icons, add like amount indicator control and sort amojis by data-count
    document.querySelectorAll("div.post").forEach((postNode) => {
        updateLikeCounter(postNode);
        updateLikeIcon(postNode);
        likesAmountIndicatorControl(postNode);
        sortEmojiList(postNode);
    })
})
