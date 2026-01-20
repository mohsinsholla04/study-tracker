function showAddForm(form, formBtn) {
    formBtn.onclick = () => {
        form.hidden = false;
        formBtn.hidden = true;
        console.log("btn  clicked")
    };
}

function showDeleteForm(formContainer, deleteBtn) {
        deleteBtn.onclick = () => {
            formContainer.style.display = "flex";
        };
}

function setupHideBtn(container) {
    hideBtn = container.querySelector(".hide");
    hideBtn.onclick = () => {
        container.style.display = "none";
    };
}
function setupDeleteBtns(btns) {
    btns.forEach(btn => {
        btn.onclick = () => {
            formContainer = document.getElementById(btn.dataset.target);
            showDeleteForm(formContainer, btn);
            setupHideBtn(formContainer);
        };
    });
}
    
document.addEventListener("DOMContentLoaded", () => {
    const topicForm = document.getElementById("topic-form");
    const topicBtn = document.getElementById("add-topic-btn");
    showAddForm(topicForm, topicBtn)
    
    const chapterForm = document.getElementById("chapter-form");
    const chapterBtn = document.getElementById("add-chapter-btn");
    showAddForm(chapterForm, chapterBtn)


    // DELETE 
    const subjectFormCont = document.getElementById("subject-overlay");
    const subjectDeleteBtn = document.getElementById("delete-subject");
    showDeleteForm(subjectFormCont, subjectDeleteBtn)
    setupHideBtn(subjectFormCont)
    
    const chaptersBtns = document.querySelectorAll(".delete_chapter_btn")
    setupDeleteBtns(chaptersBtns)
    
    const topicsBtns = document.querySelectorAll(".delete_topic_btn")
    setupDeleteBtns(topicsBtns)

    // Custom Select
    const triggers = document.querySelectorAll(".select-trigger");
    triggers.forEach(trigger => {
        trigger.addEventListener("click", () => {
            const parent = trigger.parentElement;
            parent.classList.toggle("open");

            options = document.querySelectorAll(".option");
            options.forEach(option => {
                option.addEventListener("click", () => {
                    const topicId = option.dataset.value;
                    const assignForm = option.closest("form");
                    const hiddenInput = assignForm.querySelector("input[name='topic_id']");

                    hiddenInput.value = topicId;

                    trigger.innerText = option.innerText;

                    parent.classList.toggle("open");
                })
            })
        })
    })
})