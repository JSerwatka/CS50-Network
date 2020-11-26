document.addEventListener('DOMContentLoaded', function() {
    // Init posts
    document.querySelectorAll("div.post").forEach((postNode) => {
        likePostControl(postNode);
        editPostControl(postNode);
        deletePostControl(postNode);
        updatePostLikeIcon(postNode);
        updateLikeCounter(postNode);
        sortEmojiList(postNode);
        likesAmountIndicatorControl(postNode);
        likePanelAnimationControl(postNode);
        showMoreButtonControl(postNode);
        showHideComments(postNode);
        settingsDropdownControl(postNode);
    });

    // Init comments
    document.querySelectorAll("div.comment").forEach((commentNode) => {
        likeCommentControl(commentNode);
        editCommentControl(commentNode);
        deleteCommentControl(commentNode);
        updateCommentLikeIcon(commentNode);
        updateLikeCounter(commentNode);
        sortEmojiList(commentNode);
        likesAmountIndicatorControl(commentNode);
        likePanelAnimationControl(commentNode);
        showMoreButtonControl(commentNode);
        settingsDropdownControl(commentNode);
    });

    window.addEventListener("resize", () => {
        document.querySelectorAll("div.post").forEach((postNode) => {
            showMoreButtonControl(postNode);
        })

        document.querySelectorAll("div.comment").forEach((commentNode) => {
            showMoreButtonControl(commentNode);
        })
    })
});
