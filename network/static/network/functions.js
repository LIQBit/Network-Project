function toggleLiked(postId) {
    const userId = JSON.parse(document.getElementById('user-id').textContent);
    const likesCount = getElement(postId, '.likes-count');
    const likeButton = getElement(postId, '.like-button > i.fa');

    fetch(`/post/${postId}`, {
        method: 'PUT',
        body: JSON.stringify({
            userId,
            postId,
        }),
    })
        .then(() => {
            if (likeButton.classList.contains('fa-heart-o')) {
                likeButton.classList.remove('fa-heart-o');
                likeButton.classList.add('fa-heart');
                likesCount.innerHTML = parseInt(likesCount.textContent) + 1;                
            }

            else {
                likeButton.classList.add('fa-heart-o');
                likeButton.classList.remove('fa-heart');
                likesCount.innerHTML = parseInt(likesCount.textContent) - 1;
            }
        })

        .catch((error) => {
            console.log('Error:', error);
        });

}

function editPost(postId) {
    const editButton = getElement(postId, '.edit-button');
    const postContainer = getElement(postId, '.post-container');

    const paragraph =
        postContainer.querySelector('p') !== null && 
        typeof postContainer.querySelector('p') !== 'undefined';
    
    toggleButton(editButton);

    if (editButton.innerHTML === 'Save' && paragraph) {
        openTextArea(postId, postContainer);
    }
    else{
        const body = openParagraph(postId, postContainer);
        sendUpdate(postId, body);
    }
    
}

function sendUpdate(postId, body) {
    fetch(`/post/${postId}`, {
        method: 'PUT',
        body: JSON.stringify({
            body,
        }),
    }).catch((error) => {
        console.log('Error:', error);
    });
}


function getElement(postId, className) {
    const elementNodeList = Array.from(document.querySelectorAll(className));
    const element = elementNodeList.filter((element) => element.id === postId)[0];
    return element;
}

function toggleButton(editButton) {
    if (editButton.innerText === 'Edit') {
        editButton.classList.remove('blue');
        editButton.classList.add('red');
        editButton.innerText = 'Save';
    }
    else {
        editButton.classList.remove('red');
        editButton.classList.add('blue');
        editButton.innerText = 'Edit';
    }
}

function openTextArea(postId, postContainer) {
    const postBody = getElement(postId, '.post-body');
    const textArea1 = document.createElement('textarea');

    textArea1.classList.add('form-control');
    postContainer.removeChild(postBody);
    textArea1.id = postId;
    textArea1.innerText = postBody.innerText;
    postContainer.appendChild(textArea1);
}

function openParagraph(postId, postContainer) {
    const classNames = ['card-text', 'post-body'];
    const paragraph1 = document.createElement('p');
    paragraph1.classList.add(...classNames);

    const textArea1 = getElement(postId, 'textarea');
    const textContent = textArea1.value;
    postContainer.removeChild(textArea1);

    paragraph1.id = postId;
    paragraph1.innerText = textContent;
    postContainer.appendChild(paragraph1);

    return textContent;
}
