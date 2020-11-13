document.addEventListener('DOMContentLoaded', function() {
    /* Update all:
        * like counters
        * like icons
        * add like amount indicator control
        * sort emojis by data-count 
        * show more/less post content buttons
    */
    document.querySelectorAll("div.post").forEach((postNode) => {
        updateLikeCounter(postNode);
        updateLikeIcon(postNode);
        likesAmountIndicatorControl(postNode);
        sortEmojiList(postNode);
        showMoreButtonControl(postNode);
        deletePostControl(postNode);
        likeHandling(postNode);
        editPostControl(postNode);
        likePanelAnimationControl(postNode);
    });

    // document.querySelectorAll("div.comment").forEach((commentNode) => {
    //     updateLikeCounter(commentNode);
    //     updateLikeIcon(commentNode);
    //     likesAmountIndicatorControl(commentNode);
    //     sortEmojiList(commentNode);
    //     showMoreButtonControl(commentNode);
    //     deleteCommentControl(commentNode);
    //     likeHandling(commentNode);
    //     editCommentControl(commentNode);
    //     likePanelAnimationControl(commentNode);
    // });

    window.addEventListener("resize", () => {
        document.querySelectorAll("div.post").forEach((postNode) => {
            showMoreButtonControl(postNode);
        })
    })
});
