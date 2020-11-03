document.addEventListener('DOMContentLoaded', function() {
    editPostControl();
    likePanelAnimationControl();
    likeHandling();
    likesAmountIndicatorControl();
    // Update all like counters and icons 
    document.querySelectorAll("div.post").forEach((postNode) => {
        updateLikeCounter(postNode)
        updateLikeIcon(postNode);
    })
})
