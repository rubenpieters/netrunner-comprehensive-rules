function closeToc() {
    const tocElement = document.getElementById("RulesToc");
    tocElement.style.width = "0em";
    tocElement.style.overflow = "hidden";
    tocElement.style.padding = "0em";
    const contentElement = document.getElementById("RulesContent");
    contentElement.style.marginLeft = "1.6em";
    contentElement.style.marginTop = "1.5em";
    const tocOpenElement = document.getElementById("TocOpen");
    tocOpenElement.style.visibility = "visible";
    const tocCloseElement = document.getElementById("TocClose");
    tocCloseElement.style.visibility = "hidden";
}

function openToc() {
    const tocElement = document.getElementById("RulesToc");
    tocElement.style.width = "15em";
    tocElement.style.overflow = "scroll";
    tocElement.style.padding = "0.6em";
    const contentElement = document.getElementById("RulesContent");
    contentElement.style.marginLeft = "17em";
    contentElement.style.marginTop = "0px";
    const tocOpenElement = document.getElementById("TocOpen");
    tocOpenElement.style.visibility = "hidden";
    const tocCloseElement = document.getElementById("TocClose");
    tocCloseElement.style.visibility = "visible";
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
