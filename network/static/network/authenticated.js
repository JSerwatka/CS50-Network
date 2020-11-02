document.addEventListener('DOMContentLoaded', function() {
    editPostControl();
    likePanelAnimationControl();
    likeHandling()

    // Update all like counters and icons 
    document.querySelectorAll("div.post").forEach((postNode) => {
        updateLikeCounter(postNode, 0)
        updateLikeIcon(postNode);
    })


})
