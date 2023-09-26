addEventListener("load", (event) => {
    const urlParams = new URLSearchParams(window.location.search);
    const ruleID = urlParams.get('r');
    document.getElementById(ruleID).scrollIntoView();
});

// Prevent reloading page while following rules links
// The rule link still appears in the user's navigation bar to copy and paste 
const $elems = document.querySelectorAll('a.RuleLink')
var elems = Array.from($elems)
elems.map(a => {
    a.onclick = (e) => {
        e.preventDefault()
        history.replaceState(null, null, a.href)
    }
})