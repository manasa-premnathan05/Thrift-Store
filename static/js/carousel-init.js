const myCarousel = document.querySelector('#productCarousel');
const carousel = new bootstrap.Carousel(myCarousel, {
  interval: false, // Disable auto sliding
  ride: false,     // Only slide on user action
  wrap: true,      // Wrap to the first slide after the last
  touch: true,     // Enable touch events for mobile
  keyboard: true   // Enable keyboard navigation
});
