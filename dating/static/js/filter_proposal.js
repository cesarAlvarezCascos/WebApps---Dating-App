document.addEventListener("DOMContentLoaded", function () {
    // Get filter dropdowns and lists
    const proposedFilter = document.getElementById("proposed-filter");
    const receivedFilter = document.getElementById("received-filter");
    const proposedList = document.getElementById("proposed-dates-list");
    const receivedList = document.getElementById("received-dates-list");

    // Function to filter proposals
    function filterProposals(filter, list) {
        const status = filter.value;
        const proposals = list.querySelectorAll(".proposal-card");

        proposals.forEach((proposal) => {
            if (status === "all") {
                proposal.style.display = "block"; // Show all
            } else if (proposal.classList.contains(status)) {
                proposal.style.display = "block"; // Show matching
            } else {
                proposal.style.display = "none"; // Hide others
            }
        });
    }

    // Event listeners for filter dropdowns
    proposedFilter.addEventListener("change", () => filterProposals(proposedFilter, proposedList));
    receivedFilter.addEventListener("change", () => filterProposals(receivedFilter, receivedList));
});



