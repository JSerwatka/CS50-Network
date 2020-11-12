document.addEventListener('DOMContentLoaded', function() {
    editPostControl();
    likePanelAnimationControl();
    likeHandling();
    
    /* Update all:
        * like counters
        * like icons
        * add like amount indicator control
        * sort amojis by data-count 
    */
    document.querySelectorAll("div.post").forEach((postNode) => {
        updateLikeCounter(postNode);
        updateLikeIcon(postNode);
        likesAmountIndicatorControl(postNode);
        sortEmojiList(postNode);
    });
});
