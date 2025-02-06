// @ts-check

// Ensure proper aria-landmarks
parent.document.querySelector(".stAppViewContainer")?.setAttribute("role", "main");
// TO DO: May need to shift this element if adding a <footer>


// Top menu - multiple accessibility issues
(() => {

    /** @type {HTMLButtonElement | null} */
    let menuButton = parent.document.querySelector("#MainMenu button");

    // Give menu button accessible text
    menuButton?.setAttribute("aria-label", "Menu");

    // Make menu button toggleability accessible
    menuButton?.setAttribute("aria-expanded", "false");
    menuButton?.setAttribute("aria-controls", "bui1");
    menuButton?.addEventListener("click", () => {
        const expanded = menuButton?.getAttribute("aria-expanded") === "true";
        if (expanded) {
            menuButton?.setAttribute("aria-expanded", "false");
            parent.document.querySelector("#bui1")?.remove();
        } else {
            menuButton?.setAttribute("aria-expanded", "true");
            window.setTimeout(initMenu, 200);
        }
    });

    // Make menu options accessible
    const initMenu = () => {
        let dropDown = parent.document.querySelector("#bui1");
        let menuItems = dropDown?.querySelectorAll("li > span:nth-child(1)");

        if (!dropDown) {
            return;
        }

        // move drop-down to correct position for tab-order
        parent.document.querySelector("header")?.appendChild(dropDown);

        // prevent moving focus from being blocked
        parent.document.querySelector("#root > div:nth-child(2) > div")?.remove();

        // give menu items button roles
        menuItems?.forEach((menuItem) => {
            if (menuItem.textContent === "Developer options") {
                return;
            }
            menuItem.setAttribute("role", "button");
            menuItem.setAttribute("tabindex", "0");
        });

        // remove tabindex from anything that shouldn't have it
        let rogueTabStops = dropDown.querySelectorAll("ul[tabindex]");
        rogueTabStops.forEach((element) => {
            element.removeAttribute("tabindex");
        });

        // keep focus on toggle-button
        menuButton?.focus();

    };

})();


// Remove tabindex from main container
parent.document.querySelector(".stMain")?.removeAttribute("tabindex");
// TO DO: Could change this to "-1" if combining with a skip-to-content link


// Ensure heading links have accessible text
(() => {
    let headingLinks = parent.document.querySelectorAll("[level] a, h1 a");
    headingLinks.forEach((link) => {
        link.setAttribute("aria-label", `Jump to: ${link.closest("[level")?.textContent}`);
    });
})();


// Sidebar - multiple accessibility issues
(() => {
    /** @type {HTMLElement | null} */
    let sideBar = parent.document.querySelector(".stSidebar");
    /** @type {HTMLElement | null} */
    let closeButton = parent.document.querySelector(".stSidebar button");
    /** @type {HTMLElement | null} */
    let openButton = parent.document.querySelector('[data-testid="stSidebarCollapsedControl"] button');

    if (!sideBar) {
        return;
    }

    // Ensure open/close buttons have accessible text
    closeButton?.setAttribute("aria-label", "Collapse side panel");
    openButton?.setAttribute("aria-label", "Expand side panel");

    // Ensure open/close buttons have correct aria attributes
    sideBar.id = "stSidebar";
    closeButton?.setAttribute("aria-expanded", "true");
    closeButton?.setAttribute("aria-controls", "stSidebar");
    openButton?.setAttribute("aria-expanded", "false");
    openButton?.setAttribute("aria-controls", "stSidebar");

    // Remove incorrectly-placed aria-expanded attribute
    const checkSidebar = () => {
        window.setTimeout(() => {
            const expanded = sideBar?.getAttribute("aria-expanded") || "";
            sideBar?.removeAttribute("aria-expanded");
            const waitTime = expanded === "true" ? 1 : 200;
            window.setTimeout(() => {
                if (sideBar) {
                    sideBar.dataset.expanded = expanded;
                }
            }, waitTime);
        }, 1);
    };
    checkSidebar();

    // Move focus when one of the buttons is clicked
    closeButton?.addEventListener("click", () => {
        checkSidebar();
        window.setTimeout(() => {
            openButton?.focus();
        }, 210);
    });
    openButton?.addEventListener("click", () => {
        checkSidebar();
        window.setTimeout(() => {
            closeButton?.focus();
        }, 200);
    });

})();


// Prevent links from opening in new tab (unless it has a data-newtab attribute)
(() => {
    const newTabLlinks = parent.document.querySelectorAll('[target="_blank"]');
    newTabLlinks.forEach((link) => {
        if (!link.getAttribute("data-newtab")) {
            link.removeAttribute("target");
        }
    });
})();


// Check theme so the appropriate styling can be applied
(() => {
    const checkTheme = () => {
        if (JSON.parse(localStorage.getItem("stActiveTheme-/-v1") || "{}").name === "Dark") {
            parent.document.body.classList.add("darkmode");
        } else {
            parent.document.body.classList.remove("darkmode");
        }
    };
    checkTheme();
    parent.document.querySelector("#root > div:last-child")?.addEventListener("click", checkTheme);
})();
