/**
 * app.js — Tech News Tool frontend logic
 *
 * Responsibilities:
 *  - Fetch articles and stats from the FastAPI backend
 *  - Render the top 6 latest articles with images
 *  - Render paginated article cards for all articles
 *  - Display fetch stats and trends summary
 *  - Handle manual fetch and database cleanup button actions
 *  - Manage sidebar open/close and active nav highlighting
 */

// ---------------------------------------------------------------------------
// Constants & State
// ---------------------------------------------------------------------------

/** Number of articles shown per page in the All Articles section */
const PAGE_SIZE = 10;

/** Current page index (0-based) */
let currentPage = 0;

/** Full list of articles fetched from the API, stored for client-side pagination */
let allArticles = [];

/** Reference to the full-screen loading overlay element */
const loader = document.getElementById("loader");

/**Full list of AI generated summaries fetched from API */
let allSummaries = [];


// ---------------------------------------------------------------------------
// Sidebar helpers
// ---------------------------------------------------------------------------

/**
 * Opens the sidebar and overlay on small screens.
 */
function w3_open() {
    document.getElementById("mySidebar").style.display = "block";
    document.getElementById("myOverlay").style.display = "block";
}

/**
 * Closes the sidebar and overlay on small screens.
 */
function w3_close() {
    document.getElementById("mySidebar").style.display = "none";
    document.getElementById("myOverlay").style.display = "none";
}

/**
 * Highlights the clicked nav link and removes highlighting from all others.
 *
 * @param {string} navId - The id of the nav <a> element to mark as active.
 */
function setActiveNav(navId) {
    document.querySelectorAll(".w3-bar-block a").forEach(link => {
        link.classList.remove("w3-teal", "w3-text-white");
        link.classList.add("w3-text-black");
    });
    const active = document.getElementById(navId);
    active.classList.add("w3-text-teal");
    active.classList.remove("w3-text-black");
}


// ---------------------------------------------------------------------------
// Image helpers
// ---------------------------------------------------------------------------

/**
 * Returns an appropriate fallback image path based on the article's source name.
 * Used when an article has no image_url from the RSS feed.
 *
 * @param {string} source - The source name of the article (e.g. "TechCrunch").
 * @returns {string} Path to a local fallback image.
 */
function getFallbackImage(source) {
    const s = source.toLowerCase();
    if (s.includes("techcrunch")) return "/static/images/techcrunch.jpg";
    if (s.includes("ai news") || s.includes("ai")) return "/static/images/ainews1.png";
    return "/static/images/default.jpg";
}

/**
 * Creates and returns a styled <img> element for an article card.
 *
 * @param {Object} article - The article object from the API.
 * @returns {HTMLImageElement} A configured image element.
 */
function buildArticleImage(article) {
    const photo = document.createElement("img");
    photo.src = article.image_url || getFallbackImage(article.source);
    photo.classList = "w3-hover-opacity";
    photo.alt = article.title;
    photo.style.width = "100%";
    photo.style.height = "176px";
    photo.style.marginTop = "16px";
    photo.style.objectFit = "cover";
    return photo;
}


// ---------------------------------------------------------------------------
// Latest Articles section (top 6)
// ---------------------------------------------------------------------------

/**
 * Builds a single "latest article" tile (image + title + source/date).
 *
 * @param {Object} article - The article object from the API.
 * @returns {HTMLDivElement} A fully constructed tile element.
 */
function buildLatestTile(article) {
    const item = document.createElement("div");
    item.className = "w3-third w3-container w3-margin-bottom";

    const inner = document.createElement("div");
    inner.className = "w3-container w3-teal";
    inner.style.height = "100%";
    inner.innerHTML = `
        <h5><a href="${article.link}" target="_blank">${article.title}</a></h5>
        <p class="w3-text-black">${article.source} - ${new Date(article.published).toLocaleString()}</p>
    `;
    inner.insertBefore(buildArticleImage(article), inner.firstChild);
    item.appendChild(inner);
    return item;
}

/**
 * Renders a row of latest article tiles into a given container element.
 * Equalises tile heights after insertion so the row looks uniform.
 *
 * @param {HTMLElement} container - The DOM element to render tiles into.
 * @param {Object[]} articles - Array of article objects to render.
 */
function renderLatestRow(container, articles) {
    const tiles = articles.map(article => {
        const tile = buildLatestTile(article);
        container.appendChild(tile);
        return tile;
    });

    // Equalise heights across the row after layout
    const maxHeight = Math.max(...tiles.map(t => t.offsetHeight));
    tiles.forEach(t => { t.style.height = maxHeight + "px"; });
}

/**
 * Populates the two latest-article grid rows (3 articles each).
 *
 * @param {Object[]} articles - The full articles array from the API.
 */
function renderLatestArticles(articles) {
    renderLatestRow(document.getElementById("latest-1"), articles.slice(0, 3));
    renderLatestRow(document.getElementById("latest-2"), articles.slice(3, 6));
}


// ---------------------------------------------------------------------------
// Pagination
// ---------------------------------------------------------------------------

/**
 * Renders the current page of articles into the all-articles container,
 * then rebuilds the pagination bar to reflect the new page.
 *
 * @param {number} page - The 0-based page index to render.
 */
function renderPage(page) {
    const container = document.getElementById("all-articles-container");
    container.innerHTML = "";

    const start = page * PAGE_SIZE;
    const pageArticles = allArticles.slice(start, start + PAGE_SIZE);

    pageArticles.forEach(article => {
        const card = document.createElement("div");
        card.className = "w3-card w3-white w3-margin w3-padding";
        card.innerHTML = `
            <h5><a href="${article.link}" target="_blank">${article.title}</a></h5>
            <p class="w3-text-grey">${article.source} — ${new Date(article.published).toLocaleString()}</p>
            <p>${article.summary}</p>
        `;
        container.appendChild(card);
    });

    currentPage = page;
    buildPagination();
}

/**
 * Renders the current page of summaries into the all-summaries-container,
 * then rebuilds the pagination bar to reflect the new page.
 *
 * @param {number} page - The 0-based page index to render.
 */
function renderSummaries(page) {
    const container = document.getElementById("all-summaries-container");
    container.innerHTML = "";

    const start = page * PAGE_SIZE;
    const summaries = allSummaries.slice(start, start + PAGE_SIZE);

    summaries.forEach(summary => {
        const button = document.createElement("button");
        button.className = "collapsible";
        button.innerText = new Date(summary[2]).toLocaleString();
        const content = document.createElement("div");
        content.className = "content";
        const text = document.createElement("p");
        text.innerHTML = marked.parse(summary[1]);
        content.appendChild(text);
        container.appendChild(button);
        container.appendChild(content);
    });

    var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function () {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    }

    currentPage = page;
    buildSummaryPagination();
}

/**
 * Rebuilds the pagination button bar based on total summaries count and current page.
 * Disables the prev/next arrows when at the first or last page.
 */
function buildSummaryPagination(){
    const totalPages = Math.ceil(allSummaries.length / PAGE_SIZE);
    const bar = document.querySelector(".w3-bar");
    bar.innerHTML = "";

    // Previous arrow
    const prevDisabled = currentPage === 0 ? "w3-disabled" : "";
    bar.innerHTML += `<a href="#" class="w3-bar-item w3-button w3-hover-black ${prevDisabled}"
        onclick="if(${currentPage} > 0) renderSummaries(${currentPage - 1})">&laquo;</a>`;

    // Page number buttons
    for (let i = 0; i < totalPages; i++) {
        const active = i === currentPage ? "w3-black" : "w3-hover-black";
        bar.innerHTML += `<a href="#" class="w3-bar-item w3-button ${active}"
            onclick="renderSummaries(${i})">${i + 1}</a>`;
    }

    // Next arrow
    const nextDisabled = currentPage === totalPages - 1 ? "w3-disabled" : "";
    bar.innerHTML += `<a href="#" class="w3-bar-item w3-button w3-hover-black ${nextDisabled}"
        onclick="if(${currentPage} < ${totalPages - 1}) renderSummaries(${currentPage + 1})">&raquo;</a>`;
}

/**
 * Rebuilds the pagination button bar based on total article count and current page.
 * Disables the prev/next arrows when at the first or last page.
 */
function buildPagination() {
    const totalPages = Math.ceil(allArticles.length / PAGE_SIZE);
    const bar = document.querySelector(".w3-bar");
    bar.innerHTML = "";

    // Previous arrow
    const prevDisabled = currentPage === 0 ? "w3-disabled" : "";
    bar.innerHTML += `<a href="#" class="w3-bar-item w3-button w3-hover-black ${prevDisabled}"
        onclick="if(${currentPage} > 0) renderPage(${currentPage - 1})">&laquo;</a>`;

    // Page number buttons
    for (let i = 0; i < totalPages; i++) {
        const active = i === currentPage ? "w3-black" : "w3-hover-black";
        bar.innerHTML += `<a href="#" class="w3-bar-item w3-button ${active}"
            onclick="renderPage(${i})">${i + 1}</a>`;
    }

    // Next arrow
    const nextDisabled = currentPage === totalPages - 1 ? "w3-disabled" : "";
    bar.innerHTML += `<a href="#" class="w3-bar-item w3-button w3-hover-black ${nextDisabled}"
        onclick="if(${currentPage} < ${totalPages - 1}) renderPage(${currentPage + 1})">&raquo;</a>`;
}


// ---------------------------------------------------------------------------
// Stats section
// ---------------------------------------------------------------------------

/**
 * Populates the Recent Stats panel with fetch metadata and trends summary.
 *
 * @param {Object} data - The full API response object from GET /articles.
 * @param {number} data.total - Total article count in the database.
 * @param {string} data.last_fetch - ISO timestamp of the most recent fetch.
 * @param {number} data.new_articles - Number of new articles added in the last fetch.
 * @param {string} data.trends_summary - Dash-delimited trends string from the fetcher.
 */
function renderStats(data) {
    document.getElementById("articles-found").innerHTML =
        `<b>Total Articles:</b> ${data.total}`;
    document.getElementById("last-fetch").innerHTML =
        `<b>Last Fetch:</b> ${new Date(data.last_fetch).toLocaleString()}`;
    document.getElementById("new-articles").innerHTML =
        `<b>New Articles Inserted:</b> ${data.new_articles}`;
    document.getElementById("ai-summary").innerHTML =
        marked.parse(data.ai_summary);

    const trendsEl = document.getElementById("common-trends");
    trendsEl.innerHTML = "";
    const trends = data.trends_summary.split("-").slice(1);
    trends.forEach(trend => {
        const p = document.createElement("p");
        p.textContent = `• ${trend.trim()}`;
        trendsEl.appendChild(p);
    });
}


// ---------------------------------------------------------------------------
// API actions
// ---------------------------------------------------------------------------

/**
 * Loads all articles from GET /articles, stores them in allArticles,
 * then renders the latest tiles, paginated cards, and stats panel.
 */
async function loadArticles() {
    const response = await fetch("/articles");
    const data = await response.json();
    allArticles = data.articles;

    renderLatestArticles(allArticles);
    renderPage(0);
    renderStats(data);
}

/**
 * Loads all the summaries from GET /summaries, stores them in allSummaries,
 * then renders the summaries in collapsibles sorted by date created.
 */
async function loadSummaries() {
    const response = await fetch("/summaries");
    const data = await response.json();
    allSummaries = data;

    renderSummaries(0);
}

/**
 * Generates an AI summary for the 10 most recent articles.
 */
async function generateSummary() {
    loader.classList.remove('loader-hidden');
    const response = await fetch("/articles/summary");
    const data = await response.json();
    document.getElementById("ai-summary").innerHTML =
        marked.parse(data.ai_summary);
    loader.classList.add('loader-hidden');
}

/**
 * Triggers a fresh RSS fetch via POST /fetch, shows the loader during the
 * request, then reloads the page so all sections reflect the new data.
 */
async function fetchArticles() {
    loader.classList.remove('loader-hidden');
    const response = await fetch("/fetch");
    const data = await response.json();
    console.log(data);
    loadArticles();
    loader.classList.add('loader-hidden');
    window.location.reload();
}

/**
 * Triggers the database cleanup via POST /cleanup and displays the result
 * message returned by the API below the cleanup button.
 */
async function runCleanup() {
    loader.classList.remove('loader-hidden');
    const response = await fetch("/cleanup", { method: "POST" });
    const data = await response.json();
    document.getElementById("cleanup-result").textContent = data.message;
    loader.classList.add('loader-hidden');
}


// ---------------------------------------------------------------------------
// Initialisation
// ---------------------------------------------------------------------------

// Load articles when the page first opens
loadArticles();

// Load sumamries when the page first opens
loadSummaries();

// Hide the loader spinner once the full page has loaded
window.addEventListener("load", () => {
    loader.classList.add("loader-hidden");
});

//AI Summary Collapsible
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function () {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.maxHeight) {
            content.style.maxHeight = null;
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
        }
    });
}