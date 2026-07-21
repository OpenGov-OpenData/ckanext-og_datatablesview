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

    // Serialize the per-column prefix/suffix inputs into the single hidden
    // column_prefixes / column_suffixes fields on submit. The column ids are
    // dynamic, so we can't POST one field per column; instead we send a JSON
    // map keyed by column id, which the matching validator decodes.
    function serializeAffixes(inputClass, hiddenSelector){
      let hiddenField = $(hiddenSelector);
      if (!hiddenField.length) {
        return;
      }
      hiddenField.closest('form').on('submit', function(){
        let affixes = {};
        $(inputClass).each(function(){
          let colid = $(this).data('colid');
          let val = $(this).val();
          if (colid !== undefined && val !== '') {
            affixes[colid] = val;
          }
        });
        hiddenField.val(JSON.stringify(affixes));
      });
    }
    serializeAffixes('.dt-col-prefix', '#field-column_prefixes');
    serializeAffixes('.dt-col-suffix', '#field-column_suffixes');
  });
});