document.addEventListener("DOMContentLoaded", function () {

    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");

    if (!themeToggle || !themeIcon) {
        return;
    }

    const savedTheme =
        localStorage.getItem("playguide-theme") || "dark";

    document.documentElement.setAttribute(
        "data-bs-theme",
        savedTheme
    );

    updateThemeIcon(savedTheme);


    themeToggle.addEventListener("click", function () {

        const currentTheme =
            document.documentElement.getAttribute("data-bs-theme");

        const newTheme =
            currentTheme === "dark" ? "light" : "dark";

        document.documentElement.setAttribute(
            "data-bs-theme",
            newTheme
        );

        localStorage.setItem(
            "playguide-theme",
            newTheme
        );

        updateThemeIcon(newTheme);

    });


    function updateThemeIcon(theme) {

        if (theme === "dark") {
            themeIcon.textContent = "\u2600\uFE0F";
        } else {
            themeIcon.textContent = "\uD83C\uDF19";
        }

    }

});