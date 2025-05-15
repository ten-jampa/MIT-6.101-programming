
function enableMultiStepDiagrams() {
  document.querySelectorAll(".multistep:not(.converted)").forEach(function (container) {
    container.classList.add('converted');
    
    // these functions are no-ops unless this is a side-by-side code demo
    /**
     * @param where  string, one of 'before', 'after', or 'in'
     * @param line_number_or_range  string, either '<lineNumber>' or '<start>-<end>' for a range, 1-based.
     */
    var highlightLine = function(where, line_number_or_range) {};
    var resetLineHighlights = function() {};

    if (container.hasAttribute('data-side-by-side-code')) {
      // we can't initialize side-by-side code highlighting until after the syntax-highlighting Javascript has run,
      // so defer a bit
      setTimeout(function() {
        // lines is an array of elements corresponding to code lines in the code block identified by data-code
        // Warning: 1-based indexing!!!  so lines[0] is always undefined, and lines[1] is the line numbered 1 in the UI
        const lines = [];

        const code = container.nextElementSibling;
        code.querySelectorAll(".catsoop-code-line").forEach(function (b) {
          const lineNumber = parseInt(b.children[0].getAttribute("data-line-number"));
          lines[lineNumber] = b;
        });

        highlightLine = function(where, line_number_or_range) {
          try {
            line_numbers = line_number_or_range.split('-').map(s => parseInt(s));
            first = line_numbers[0];
            last = line_numbers.length > 1 ? line_numbers[1] : first;
            if (where === 'before') {
              lines[first].style['border-top'] = '3px solid yellow';
            } else if (where === 'after') {
              if (last+1 < lines.length) {
                lines[last+1].style['border-top'] = '3px solid yellow';
              } else {
                lines[last].style['border-bottom'] = '3px solid yellow';
              }
            } else if (where === 'in') {
              for (var lineNum = first; lineNum <= last; ++lineNum) {
                  lines[lineNum].style.backgroundColor = '#FFFFA0';
              }
            }
          } catch (e) {
            console.error(`cannot highlight ${where} line ${line_number_or_range}`)
            console.error(e);
          }
        };

        resetLineHighlights = function() {
          lines.forEach(line => {
            line.style.backgroundColor = 'inherit';
            line.style["border-top"] = "3px solid transparent";
          });
          if (lines.length) {
            // only the last element's bottom is used
            lines[lines.length-1].style["border-bottom"] = "3px solid transparent";
          }
        };

        goToStep(0);        
      }, 50);
    }


    const stepDivs = [...container.querySelectorAll('.step')];

    var currentStep = null;
    var lastStep = stepDivs.length - 1;

    function goToStep(ix) {
      var oldStep = currentStep;
      currentStep = Math.max(0, Math.min(lastStep, ix));

      var oldDiv = stepDivs[oldStep];
      var newDiv = stepDivs[currentStep];

      if (oldStep !== null) {
        oldDiv.classList.remove('active');
        resetLineHighlights();
      }
      newDiv.classList.add('active');

      for (const where of ['before', 'after', 'in']) {
        const value = newDiv.getAttribute(`data-${where}-line`);
        if (value) {
          highlightLine(where, value);
        }
      }

      var noback = currentStep === 0;
      var noforward = currentStep === lastStep;
      buttonFirst.disabled = noback;
      buttonBack.disabled = noback;
      buttonNext.disabled = noforward;
      buttonLast.disabled = noforward;
    }

    const buttons = document.createElement("div");
    buttons.classList.add('multistep-buttons')
    const buttonFirst = document.createElement("button");
    buttonFirst.innerText = "<< First Step";
    buttonFirst.onclick = function () {
      goToStep(0);
    };
    const buttonBack = document.createElement("button");
    buttonBack.innerText = "< Previous Step";
    buttonBack.onclick = function () {
      goToStep(currentStep - 1);
    };
    const buttonNext = document.createElement("button");
    buttonNext.innerText = "Next Step >";
    buttonNext.onclick = function () {
      goToStep(currentStep + 1);
    };
    const buttonLast = document.createElement("button");
    buttonLast.innerText = "Last Step >>";
    buttonLast.onclick = function () {
      goToStep(lastStep);
    };

    buttons.append(buttonFirst);
    buttons.append(buttonBack);
    buttons.append(buttonNext);
    buttons.append(buttonLast);
    container.prepend(buttons);

    // tell CSS that we have created the buttons,
    // so only one step will be visible at a time
    container.classList.add('buttons-enabled');

    stepDivs.forEach((stepDiv, ix) => {
      stepDiv.setAttribute("data-explanation-for-step", "" + ix);
      // apparently the background color messes with floating?
      stepDiv.querySelectorAll("pre").forEach(function (b) {
        b.style.backgroundColor = "inherit";
        b.querySelectorAll("code").forEach(function (b2) {
          b2.style.backgroundColor = "inherit";
        });
      });
      const stepLabel = stepDiv.querySelector('.step-label');
      if (stepLabel) {
        const prefix = stepLabel.textContent.trim() || 'STEP';
        stepLabel.innerText = `${prefix} ${ix + 1}`;
      }
    });

    goToStep(0);

  });
}

document.addEventListener("DOMContentLoaded", enableMultiStepDiagrams);
