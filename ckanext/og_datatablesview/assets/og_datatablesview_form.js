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

    // Serialize per-column inputs into a single hidden field on submit.
    // The column ids are dynamic, so we can't POST one field per column;
    // instead we send a JSON map keyed by column id, which the matching
    // validator decodes. getValue(el) returns the value to store, or
    // undefined to skip that column.
    function serializeColumnInputs(inputClass, hiddenSelector, getValue) {
      let hiddenField = $(hiddenSelector);
      if (!hiddenField.length) {
        return;
      }
      hiddenField.closest('form').on('submit', function () {
        let result = {};
        $(inputClass).each(function () {
          let colid = $(this).data('colid');
          let val = getValue(this);
          if (colid !== undefined && val !== undefined) {
            result[colid] = val;
          }
        });
        hiddenField.val(JSON.stringify(result));
      });
    }
    serializeColumnInputs('.dt-col-prefix',     '#field-column_prefixes',   function (el) { let v = $(el).val(); return v !== '' ? v : undefined; });
    serializeColumnInputs('.dt-col-suffix',     '#field-column_suffixes',   function (el) { let v = $(el).val(); return v !== '' ? v : undefined; });
    serializeColumnInputs('.dt-col-thousands',  '#field-column_thousands',  function (el) { return $(el).is(':checked') ? '1' : undefined; });
    serializeColumnInputs('.dt-col-alignments', '#field-column_alignments', function (el) { return $(el).is(':checked') ? '1' : undefined; });
  });
});