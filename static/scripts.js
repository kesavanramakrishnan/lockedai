/*!
 * Start Bootstrap - Grayscale v7.0.6 (https://startbootstrap.com/theme/grayscale)
 * Copyright 2013-2023 Start Bootstrap
 * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-grayscale/blob/master/LICENSE)
 */
//
// Scripts
//


let sessionButton = document.getElementById("sessionButton");
let videoStream = document.getElementById("videoStream");
let trackFocus = document.getElementById("trackFocus");
let trackSleep = document.getElementById("trackSleep");
let emailInput = document.getElementById("emailInput");
let streamStarted = false;

sessionButton.addEventListener("click", toggleSession);

window.addEventListener("DOMContentLoaded", (event) => {
  // Navbar shrink function
  var navbarShrink = function () {
    const navbarCollapsible = document.body.querySelector("#mainNav");
    if (!navbarCollapsible) {
      return;
    }
    if (window.scrollY === 0) {
      navbarCollapsible.classList.remove("navbar-shrink");
    } else {
      navbarCollapsible.classList.add("navbar-shrink");
    }
  };

  // Shrink the navbar
  navbarShrink();

  // Shrink the navbar when page is scrolled
  document.addEventListener("scroll", navbarShrink);

  // Activate Bootstrap scrollspy on the main nav element
  const mainNav = document.body.querySelector("#mainNav");
  if (mainNav) {
    new bootstrap.ScrollSpy(document.body, {
      target: "#mainNav",
      rootMargin: "0px 0px -40%",
    });
  }

  // Collapse responsive navbar when toggler is visible
  const navbarToggler = document.body.querySelector(".navbar-toggler");
  const responsiveNavItems = [].slice.call(
    document.querySelectorAll("#navbarResponsive .nav-link")
  );
  responsiveNavItems.map(function (responsiveNavItem) {
    responsiveNavItem.addEventListener("click", () => {
      if (window.getComputedStyle(navbarToggler).display !== "none") {
        navbarToggler.click();
      }
    });
  });
});

function toggleSession() {
  if(emailInput.value.length > 10){
    if (!streamStarted) {
      const data = {
        "user_email": emailInput.value,
        "focus": trackFocus.checked,
        "sleep": trackSleep.checked,
      };

      fetch("http://127.0.0.1:5000/receive_data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })
        .then((response) => response.text())
        .then((data) => console.log(data))
        .catch((error) => console.error("Error:", error));

      videoStream.src = "http://127.0.0.1:5000/video_feed";
      sessionButton.textContent = "End Session";
      streamStarted = true;

      fetch("http://127.0.0.1:5000/resume_stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.text())
        .then((data) => console.log(data))
        .catch((error) => console.error("Error:", error));
    } else {
      videoStream.src = "";
      sessionButton.textContent = "Start Session";
      streamStarted = false;
      fetch("http://127.0.0.1:5000/pause_stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.text())
        .then((data) => showModal(data))
        .catch((error) => console.error("Error:", error));
    }
  }
}



  function showModal(data) {
    document.getElementById("chartModal").style.display = "flex";
    renderChart(data);
  }

  function closeModal() {
    efficiencyChart.destroy();
    document.getElementById("chartModal").style.display = "none";
  }

  let efficiencyChart

  function renderChart(data) {
    const parsed = JSON.parse(data);
    const combined = [parsed.zero, parsed.one];
    console.log(combined);
    const labels = ["Unfocused Time", "Focused Time"];
    const ctx = document.getElementById("efficiencyChart").getContext("2d");
    efficiencyChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Efficiency",
            data: combined,
            backgroundColor: [
              'rgb(255, 99, 132)',
              'rgb(54, 162, 235)',
            ],
            hoverOffset: 4,
          },
        ],
      },
      options: {
        plugins:{
          title:{
            display: true,
            text: "How Focused Were You?"
          }
        },
        responsive: true,
      },
    });
  }
