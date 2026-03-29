document.addEventListener('DOMContentLoaded', function () {
  // Smooth scroll for details
  const details = document.querySelectorAll('details');
  details.forEach(detail => {
    detail.addEventListener('toggle', function () {
      if (this.open) {
        this.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  });
});