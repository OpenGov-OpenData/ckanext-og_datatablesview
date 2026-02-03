window.addEventListener('load', function(){
  $(document).ready(function(){
    let dtShowAll = $('button.dt-show-all');
    let dtHideAll = $('button.dt-hide-all');
    let dtColSelects = $('.dt-select-columns').find('input[type="checkbox"]').not('input[value="_id"]');
    $(dtShowAll).on('click', function(_event){
      $(dtColSelects).prop('checked', true).change().blur();
    });
    $(dtHideAll).on('click', function(_event){
      $(dtColSelects).prop('checked', false).change().blur();
    });
  });
});