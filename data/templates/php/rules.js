function closeToc() {
    const parent = document.querySelector("#RulesParent");
    parent.removeAttribute("data-tocopen");
}
function openToc() {
    const parent = document.querySelector("#RulesParent");
    parent.setAttribute("data-tocopen", "");
}

addEventListener("load", (event) => {
    const urlParams = new URLSearchParams(window.location.search);
    const ruleId = urlParams.get('r');
    if(ruleId) {
        document.getElementById(ruleId).scrollIntoView();
    }
});

// Prevent reloading page while following rules links
// The rule link still appears in the user's navigation bar to copy and paste 
const $elems = document.querySelectorAll('a.RuleLink')
const elems = Array.from($elems)
elems.forEach(a => {
    url = new URL(a.href);
    url.search = url.hash.replace('#', '?r=');
    url.hash = "";
    a.href = url.href;
    a.onclick = (e) => {
        // do not follow link
        e.preventDefault();

        // replace url in nav bar
        history.replaceState(null, null, a.href);

        // Replace link symbol with clipboard symbol
        navigator.clipboard.writeText(a.href);
        a.parentElement.getElementsByClassName('material-symbols-outlined')[0].innerText = "content_paste_go";
        
        // Revert back to link symbol after 1s
        setTimeout(() => {
            a.parentElement.getElementsByClassName('material-symbols-outlined')[0].innerText = "link";

        }, 1000);
    }
})
