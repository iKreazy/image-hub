document.addEventListener("DOMContentLoaded", function () {
    let isLoading = false;
    let page = 2;
    const limit = 10;
    let hasMore = true;

    function showLoadingSpinner() {
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.insertAdjacentHTML('beforeend', `
                <div class="loading-spinner"><i class="bi bi-arrow-clockwise"></i></div>
            `);
        }
    }

    function hideLoadingSpinner() {
        const spinner = document.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }

    function showEndOfPosts() {
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.insertAdjacentHTML('beforeend', `
                <div class="end-posts">End of posts</div>
            `);
        }
    }

    async function fetchImages(url, params = {}) {
        try {
            const query = new URLSearchParams(params).toString();
            const response = await fetch(`/api/v1/${url}?${query}`);
            if (response.status === 404) {
                return [];
            }
            if (!response.ok) {
                throw new Error("Error loading data");
            }
            return response.json();
        } catch (error) {
            console.error("Request error:", error);
            return [];
        }
    }

    function appendHtmlElements(htmlElements) {
        const container = document.querySelector('.masonry-container');
        if (container && htmlElements) {
            htmlElements.forEach(html => {
                container.insertAdjacentHTML('beforeend', html);
            });
        }
    }

    function processImageResponse(jsonData, htmlData) {
        let newImages = [];
        let jsonResults = [];
        let htmlResults = [];

        if (window.pageData.key === "index") {
            jsonResults = jsonData;
            htmlResults = htmlData;
        } else {
            jsonResults = jsonData.results || [];
            htmlResults = htmlData.results || [];
        }

        jsonResults.forEach(image => {
            if (!window.pageData.images.includes(image.id)) {
                newImages.push(image.id);
                window.pageData.images.push(image.id);
            }
        });

        if (newImages.length) {
            appendHtmlElements(htmlResults);
        } else {
            hasMore = false;
            showEndOfPosts();
        }
    }

    async function loadMoreImages() {
        if (isLoading || !hasMore) return;
        isLoading = true;
        showLoadingSpinner();

        let apiEndpoint = "";
        let params = { limit, p: page };

        switch (window.pageData.key) {
            case "index":
                apiEndpoint = "images";
                params = {exclude: window.pageData.images.join(',')};
                break;
            case "recents":
                apiEndpoint = "images/recents";
                break;
            case "category":
                apiEndpoint = `images/category/${window.pageData.categorySlug}`;
                break;
            case "account":
                apiEndpoint = `images/account/${window.pageData.username}`;
                break;
            case "account" && window.pageData.imageId !== null:
                apiEndpoint = `image/id/${window.pageData.imageId}/after`;
                break;
            default:
                hideLoadingSpinner();
                isLoading = false;
                return;
        }

        const jsonResponse = await fetchImages(apiEndpoint, { ...params });
        const htmlResponse = await fetchImages(apiEndpoint, { ...params, html: true });

        hideLoadingSpinner();
        
        if (jsonResponse && htmlResponse) {
            processImageResponse(jsonResponse, htmlResponse);
        }

        if (!jsonResponse) {
            hasMore = false;
            showEndOfPosts();
        }

        isLoading = false;
        page++;
    }

    function checkScrollPosition() {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
            loadMoreImages();
        }
    }

    window.addEventListener('scroll', checkScrollPosition);

    setInterval(() => {
        const container = document.querySelector('.masonry-container');
        if (container) {
            new Masonry(container, {percentPosition: true});
        }
    }, 500);
});
