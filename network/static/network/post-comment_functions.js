function settingsDropdownControl(node) {
    let dropdownElement = node.querySelector(".delete-edit-panel > .dropdown");

    $(window).on("resize", () => {
        if (window.innerWidth < 800) {
            dropdownElement.classList.add("dropleft");
        }
        else {
            dropdownElement.classList.remove("dropleft");
        }
    })
}


// Adds emoji to like data panel
function updateEmojiList(node, newEmojiType, previousEmojiType=null) {
    // PUT request -> update previous emoji count and visibility
    if (previousEmojiType !== null) {
        // Grab node of previous emoji
        let previousEmojiNode = node.querySelector(`.emoji-list > i[data-name=${previousEmojiType}]`);
        // Decrement its value because of emoji change
        previousEmojiNode.dataset.count -= 1;

        // If amount of emojis of this type less than 1 -> delete it from the list
        if (previousEmojiNode.dataset.count < 1) {
            previousEmojiNode.remove();
        }
    }   
    
    // PUT or POST request -> add new emoji node or update its counter
    let emojiList = node.querySelector("ul.emoji-list");
    let newEmojiNode = emojiList.querySelector(`i[data-name=${newEmojiType}]`);

    // Check if emoji already in emoji list
    // If yes - just increment the counter and refresh it
    if (newEmojiNode) {
        newEmojiNode.dataset.count = parseInt(newEmojiNode.dataset.count) + 1;
    }
    // If no - add emoji to emoji list
    else {
        let wrapper = document.createElement("div");
        wrapper.innerHTML = emojiNameToHtml(newEmojiType);
        emojiList.appendChild(wrapper.firstChild);
    }

    // Make sure that like counter has correct value
    updateLikeCounter(node);
    // Sort emojis by amount of likes
    sortEmojiList(node);
}

function updateLikeCounter(node) {
    let additionalLikes = 0;

    // Emoji tags counter
    let emojiTagCount = 0;
    // All emoji types likes counter
    let emojiTypeCount = 0;

    // Get list of emoji tags
    let emojiTagArray = Array.from(node.querySelector("ul.emoji-list").children)

    // Get sum of emoji tags and data-count values
    for (const key in emojiTagArray) {
        emojiTagCount += 1;
        emojiTypeCount += parseInt(emojiTagArray[key].dataset.count);
    }

    // Get count of additional likes
    additionalLikes = emojiTypeCount - emojiTagCount;

    if (additionalLikes > 0) {
        node.querySelector("span.like-counter").textContent = `+${additionalLikes}`;
    }
    else {
        node.querySelector("span.like-counter").textContent = ""
    }
}

// Sort emojis by amount of likes
function sortEmojiList(node) {
    let emojiList = node.querySelector("ul.emoji-list")

    if (emojiList.children.length > 1) {
        Array.from(emojiList.children)
        .sort(({dataset: {count: a}}, {dataset: {count: b}}) => parseInt(b) - parseInt(a))
        .forEach((emojiTag) => {
            emojiList.appendChild(emojiTag)
        })
    }
}

// Shows little number indicator if you hover over emoji in emoji list
function likesAmountIndicatorControl(node) {
    node.querySelectorAll(".emoji-list > i.em").forEach(emojiTag => {
        // Create a like amount indicator element
        let likesAmountIndicator = document.createElement("li");
        likesAmountIndicator.className = "likes-indicator";

        // Show like amount indicator
        emojiTag.onmouseover = (event) => {
            // Make sure that the appended child doesn't inherit this eventlistener
            if (event.target.classList.contains("em")) {
                likesAmountIndicator.innerHTML = event.target.dataset.count;
                event.target.appendChild(likesAmountIndicator);
            }
        }

        // Remove like amount indicator
        emojiTag.onmouseout = () => {
            likesAmountIndicator.remove();
        }

    })
}

function likePanelAnimationControl(node) {
    let likePanel = node.querySelector(".like-panel")
    const emojiPanel = likePanel.querySelector(".emoji-choice");
    let timeoutOut;
    let timeoutIn;

    // On hover show like-panel
    likePanel.addEventListener("mouseover", () => {
        clearTimeout(timeoutOut)
        timeoutIn = setTimeout(() => {
            emojiPanel.classList.remove("hidden");
            emojiPanel.classList.add("like-panel-in");
        }, 400)
    })

    // On hover out hide like-panel after 1s
    likePanel.addEventListener("mouseout", () => {
        clearTimeout(timeoutIn)
        timeoutOut = setTimeout(() => {
            emojiPanel.classList.remove("like-panel-in");
            emojiPanel.classList.add("hidden");
        }, 600)
    })
}

// Show show-more button if post's content overflowing
function showMoreButtonControl(node) {
    let content = node.querySelector(".content")
    let showMore;
    if (content.classList.contains("post-content")){
        showMore = content.nextElementSibling;
    }
    else {
        showMore = content.parentElement.nextElementSibling;
    }

    let isOverflowing = (content.clientWidth < content.scrollWidth)
                        || (content.clientHeight < content.scrollHeight); 

    // Text overflowing -> show show-more button and handle click event
    if (isOverflowing) {
        showMore.classList.remove("hidden")

        showMore.onclick = () => {
            // Make post content short or full height
            content.classList.remove("short");
            showMore.classList.add("hidden")
        }
    }
    // Text not overflowing -> hide show-more button
    else {
        showMore.classList.add("hidden")
    }
}

// Force to show "show more" button if overflowing in commnets
// Bootstap's collapse prevents content property from running
function showHideComments(postNode) {
    let commentButton = postNode.querySelector(".comment-button");
    let commentSection = postNode.nextElementSibling
    
    $(commentSection).on('shown.bs.collapse', () => {
        commentSection.querySelectorAll(".comment").forEach(commentNode => {
            showMoreButtonControl(commentNode);
        })
    })
}

function emojiNameToHtml(emojiType) {
    let emojiHtml;

    switch (emojiType) {
        case "like":
            emojiHtml = '<i class="em em---1" aria-role="presentation" aria-label="THUMBS UP SIGN" data-count=1 data-name="like"></i>' + gettext("Like");
            break;
        case "dislike":
            emojiHtml = '<i class="em em--1" aria-role="presentation" aria-label="THUMBS DOWN SIGN" data-count=1 data-name="dislike"></i>' + gettext("Like");
            break;
        case "smile":
            emojiHtml = '<i class="em em-smile" aria-role="presentation" aria-label="SMILING FACE WITH OPEN MOUTH AND SMILING EYES" data-count=1 data-name="smile"></i>' + gettext("Like");
            break;
        case "heart":
            emojiHtml = '<i class="em em-heart" aria-role="presentation" aria-label="HEAVY BLACK HEART" data-count=1 data-name="heart"></i>' + gettext("Like");
            break;
        case "thanks":
            emojiHtml = '<i class="em em-bouquet" aria-role="presentation" aria-label="BOUQUET" data-count=1 data-name="thanks"></i>' + gettext("Like");
            break;
        default:
            emojiHtml = '';
    }

    return emojiHtml;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}