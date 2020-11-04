document.addEventListener('DOMContentLoaded', function() {
    editPostControl();
    likePanelAnimationControl();
    likeHandling();
    
    // Update all like counters, icons and add like amount indicator control
    document.querySelectorAll("div.post").forEach((postNode) => {
        updateLikeCounter(postNode)
        updateLikeIcon(postNode);
        likesAmountIndicatorControl(postNode);
    })
})
