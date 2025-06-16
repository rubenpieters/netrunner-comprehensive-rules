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

jQuery(document).ready(function($){
    $('.Thumbnail').hover(function(){
        const data_src = $(this).children('.ThumbnailImageContainer').children('img').attr('data-src');
        $(this).children('ThumbnailImageContainer').children('img').attr('src', data_src);
    });
});

function buildPartialMatchFromWordStartExpression(searchValue) {
    return new RegExp(`(?<=^|\\s|\\>)${RegExp.escape(searchValue)}`, 'i');
};

function buildAllPartialMatchesFromWordStartExpression(searchValue) {
    return new RegExp(`(?<=^|\\s|\\>)${RegExp.escape(searchValue)}`, 'gi');
};

function buildExactMatchExpression(searchValue) {
    return new RegExp(`(?<=^)${RegExp.escape(searchValue)}(?=$)`, 'i');
};

function buildAllMatchesExpression(searchValue) {
    return new RegExp(RegExp.escape(searchValue), 'gi');
};

jQuery.fn.extractNestedTextNodes = function() {
    const textNodes = []

    this.each(function() {  
        if ($(this).get(0).nodeType === Node.TEXT_NODE && !$(this).parent().is('.RuleLinkSymbol')) {
            textNodes.push($(this))
        } else if ($(this).get(0).nodeType === Node.ELEMENT_NODE) {
            const nestedTextNodes = $(this).contents().extractNestedTextNodes()
            textNodes.push(...nestedTextNodes)
        }
    })

    return textNodes;
}

jQuery.fn.addHighlightsToRule = function(textToHighlight) {
    const allPartialMatchesFromWordStart = buildAllPartialMatchesFromWordStartExpression(textToHighlight);

    this.extractNestedTextNodes().forEach(function($node) {
        const nodeText = $node.get(0).nodeValue;

        // TODO When matches a card name that is linked to a thumbnail, the addition of the highlight span removes the highlighted words from the link
        if (allPartialMatchesFromWordStart.test(nodeText)) {
            const highlightedHTML = nodeText.replace(allPartialMatchesFromWordStart, match => `<span class="Highlight">${match}</span>`)
            const $wrapper = $('<span></span>').html(highlightedHTML);
            $node.replaceWith($wrapper.contents());
        }
    })
};

jQuery.fn.removeHighlightsFromRule = function(textToRemoveHightlight) {

    
    let textWithHighlightsRemoved = this.html().replace(buildAllMatchesExpression(`<span class="Highlight">${textToRemoveHightlight}</span>`), function(match) {
        return match.replace('<span class="Highlight">', '').replace('</span>', '');
    });
    
    this.html(textWithHighlightsRemoved);
};

// Assumes a chapter heading element is always above a rules element
jQuery.fn.findChapterHeading = function() {
    if (this.prev().is(".Chapter")) {
        return this.prev();
    } else {
        return this.prev().findChapterHeading();
    };
};

// Assumes a section heading element is always above a rules element
jQuery.fn.findSectionHeading = function() {
    if (this.prev().is(".Section")) {
        return this.prev();
    } else {
        return this.prev().findSectionHeading();
    };
};

jQuery.fn.showHeadingsForEachRule = function() {
    return this.each(function() {
        const $chapterHeading = $(this).findChapterHeading();
            $chapterHeading.show();

            const [tocChapterReference] = $chapterHeading.text().split('. ');
            $(".RulesTocList>li>a").filter(function() {
                return $(this).text().startsWith(`${tocChapterReference} `);
            }).parent().show();

            const $sectionHeading = $(this).findSectionHeading();
            $sectionHeading.show();

            const [tocSectionReference] = $sectionHeading.text().split('. ');
            $(".RulesTocList>li>a").filter(function() {
                return $(this).text().startsWith(`${tocSectionReference} `);
            }).parent().show();

            if ($(this).prev().is(".Snippet")) {
                $(this).prev().show();
            };
    });
};

jQuery(document).ready(function($) {
    // Filters available tags
    $('#SearchInput').on("keyup", function(e) {
        if (e.key === 'Enter') {
            const searchValue = $(this).val();

            if (searchValue !== '') {
                const exactMatch = buildExactMatchExpression(searchValue);

                const matchingTags = $("#SelectedTags>li").filter(function() {
                    return exactMatch.test($(this).text());
                })

                if (matchingTags.length === 0) {
                    $("main").children().hide();
                    $(".RulesTocList>li").hide();
                    
                    $("#SelectedTags").append(`<li class="CustomTag">${searchValue}</li>`);

                    const selectedTagExpressions = $.map($("#SelectedTags>li"), function(tag) {
                        return buildPartialMatchFromWordStartExpression($(tag).text());
                    });

                    const $selectedRules = $("main>.Rules").filter(function() {
                        let aRuleContainsSelectedTags = false;

                        $(this).children(".Rule").each(function() {
                            const $rule = $(this);

                            const textNodes = $(this).extractNestedTextNodes()
                            
                            const allTagsMatch = selectedTagExpressions.every((selectedTagExpression) => {
                                return textNodes.some((textNode) => {
                                    return selectedTagExpression.test(textNode.get(0).nodeValue)
                                })
                            });
                            
                            if (allTagsMatch) {            
                                $rule.addHighlightsToRule(searchValue);
                                $rule.show();
                                aRuleContainsSelectedTags = true;
                            } else {
                                $rule.hide();
                            };
                        });

                        return aRuleContainsSelectedTags;
                    })

                    $selectedRules.showHeadingsForEachRule();

                    $selectedRules.show();
                }
                
                $('#SearchInput').val('');
            };
        }
    });

    // Handles tag deselection, removing from selected tags list
    $("#SelectedTags").on('click', 'li', function() {
        const $clickedTag = $(this);
        const clickedTagText = $clickedTag.text();
        
        $clickedTag.remove();

        if ($("#SelectedTags>li").length) {
            const selectedTagExpressions = $.map($("#SelectedTags>li"), function(tag) {
                return buildPartialMatchFromWordStartExpression($(tag).text());
            });

            const $selectedRules = $("main>.Rules").filter(function() {      
                let aRuleContainsSelectedTags = false;

                $(this).children(".Rule").each(function() {
                    const $rule = $(this);
                    const textNodes = $(this).extractNestedTextNodes()

                    $rule.removeHighlightsFromRule(clickedTagText);
  
                    const allTagsMatch = selectedTagExpressions.every((selectedTagExpression) => {
                        return textNodes.some((textNode) => {
                            return selectedTagExpression.test(textNode.get(0).nodeValue)
                        })
                    });
                    
                    if (allTagsMatch) {            
                        $rule.show();
                        aRuleContainsSelectedTags = true;
                    } else {
                        $rule.hide();
                    };
                });

                return aRuleContainsSelectedTags;    
            });

            $selectedRules.showHeadingsForEachRule();

            $selectedRules.show();
        } else {   
            $("main").children().show();
            $(".RulesTocList>li").show();
            $("main>ol>li").each(function() {
                $(this).show();
                $(this).removeHighlightsFromRule(clickedTagText);
            });
        };
    });
});
