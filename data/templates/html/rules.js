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
        const data_src = $(this).children('span').children('img').attr('data-src');
        $(this).children('span').children('img').attr('src', data_src);
    });
});

function buildMatchPartialWordFromStartExpression(searchValue) {
    return new RegExp(`(?<=^|\\s)${RegExp.escape(searchValue)}`, 'i');
};

function buildMatchCompleteWordFromStartExpression(searchValue) {
    return new RegExp(`(?<=^|\\s|\\>)${RegExp.escape(searchValue)}(?=$|\\s|\\<)`, 'i');
};

function buildMatchAllCompleteWordsFromStartExpression(searchValue) {
    return new RegExp(`(?<=^|\\s|\\>)(${RegExp.escape(searchValue)})(?=$|\\s|\\<)`, 'gi');
};

jQuery.fn.addHighlightsToRule = function(textToHighlight) {
    const highlightedText = this.html().replace(buildMatchAllCompleteWordsFromStartExpression(textToHighlight), function(match) {
            return `<span style="background-color:#FFFF00;">${match}</span>`;
        });

    this.html(highlightedText);
};

jQuery.fn.removeHighlightsFromRule = function(textToRemoveHightlight) {
    let textWithHighlightsRemoved = this.html().replace(buildMatchAllCompleteWordsFromStartExpression(`<span style="background-color:#FFFF00;">${textToRemoveHightlight}</span>`), function() {
        return textToRemoveHightlight;
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
    $('#SearchInput').on("keyup", function() {
        const searchValue = $(this).val();

        if (searchValue === '') {
            $("#AvailableTags>li").hide();
        } else {
            const matchPartialWordFromStart = buildMatchPartialWordFromStartExpression(searchValue);

            $("#AvailableTags>li").filter(function() {
                const isMatch = matchPartialWordFromStart.test($(this).text());

                if (!isMatch) $(this).hide();

                return isMatch;
            }).each(function() {
                const $availableTag = $(this);
                let isNotSelected = true;

                $("#SelectedTags>li").each(function() {
                    if ($(this).text() === $availableTag.text()) {
                        isNotSelected = false;
                    };
                });

                if (isNotSelected) $availableTag.show();
            });
        };
    });

    // Handles tag selection, clearing search input, hiding available tags, and displaying selected tag
    $("#AvailableTags").on('click', 'li', function() {
        const $clickedTag = $(this);

        $('#SearchInput').val('');

        $("main").children().hide();
        $(".RulesTocList>li").hide();
        $("#AvailableTags>li").hide();

        $("#SelectedTags").append(`<li>${$clickedTag.text()}</li>`);


        const $selectedRules = $("main>.Rules").filter(function() {
            let aRuleContainsSelectedTags = false;

            $(this).children(".Rule").each(function() {
                const $rule = $(this);
                
                let allTagsMatch = true;
                
                $("#SelectedTags>li").each(function() {
                    const matchCompleteWordFromStart = buildMatchCompleteWordFromStartExpression($(this).text());
                    
                    if (!matchCompleteWordFromStart.test($rule.html())) {
                        allTagsMatch = false;
                    } else {
                        $rule.addHighlightsToRule($(this).text());
                    }
                })
                
                if (allTagsMatch) {            
                    $rule.show();
                    aRuleContainsSelectedTags = true;
                } else {
                    $rule.hide();
                }
            })

            return aRuleContainsSelectedTags;
        })

        $selectedRules.showHeadingsForEachRule();

        $selectedRules.show();
    });

    // Handles tag deselection, hiding in selected and displaying in available if current search input matches
    $("#SelectedTags").on('click', 'li', function() {
        const $clickedTag = $(this);
        const tagText = $clickedTag.text();

        $clickedTag.remove();

        const searchValue = $('#SearchInput').val();

        // If search input is not empty & matches deselected tag, show in available tags
        if (searchValue !== '') {
            const matchPartialWordFromStart = buildMatchPartialWordFromStartExpression(searchValue);

            $("#AvailableTags>li").filter(function() {
                return $(this).text() === tagText && matchPartialWordFromStart.test($(this).text());
            }).show();
        };

        if ($("#SelectedTags>li").length) {
            const $selectedRules = $("main>.Rules").filter(function() {      
                let aRuleContainsSelectedTags = false;

                $(this).children(".Rule").each(function() {
                    const $rule = $(this);

                    $rule.removeHighlightsFromRule($clickedTag.text());
                    
                    let allTagsMatch = true;
                    
                    $("#SelectedTags>li").each(function() {
                        const matchCompleteWordFromStart = buildMatchCompleteWordFromStartExpression($(this).text());
                        
                        if (!matchCompleteWordFromStart.test($rule.html())) {
                            allTagsMatch = false;
                        };
                    });
                    
                    if (allTagsMatch) {                                
                        $rule.show();
                        aRuleContainsSelectedTags = true;
                    } else {
                        $rule.hide();
                    }
                })

                return aRuleContainsSelectedTags;    
            });

            $selectedRules.showHeadingsForEachRule();

            $selectedRules.show();
        } else {   
            $("main").children().show();
            $(".RulesTocList>li").show();
            $("main>ol>li").each(function() {
                $(this).show();
                $(this).removeHighlightsFromRule($clickedTag.text());
            });
        };
    });
});
