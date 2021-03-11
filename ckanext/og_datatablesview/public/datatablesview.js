var run_query = function(params, format) {
  var form = $('#filtered-datatables-download');
  var p = $('<input name="params" type="hidden"/>');
  p.attr("value", JSON.stringify(params));
  form.append(p);
  var f = $('<input name="format" type="hidden"/>');
  f.attr("value", format);
  form.append(f);
  form.submit();
}

//main
this.ckan.module('datatables_view', function (jQuery) {
  return {
    initialize: function() {
      var datatable = jQuery('#dtprv').DataTable({});
      var display_export_button = document.getElementById('dtprv').getAttribute('display-export-button')
      if (display_export_button === 'true'){
        // Adds download dropdown to buttons menu
        datatable.button().add(1, {
          text: 'Export',
          extend: 'collection',
          buttons: [{
            text: 'CSV',
            action: function (e, dt, button, config) {
              var params = datatable.ajax.params();
              params.visible = datatable.columns().visible().toArray();
              run_query(params, 'csv');
            }
          }, {
            text: 'TSV',
            action: function (e, dt, button, config) {
              var params = datatable.ajax.params();
              params.visible = datatable.columns().visible().toArray();
              run_query(params, 'tsv');
            }
          }, {
            text: 'JSON',
            action: function (e, dt, button, config) {
              var params = datatable.ajax.params();
              params.visible = datatable.columns().visible().toArray();
              run_query(params, 'json');
            }
          }, {
            text: 'XML',
            action: function (e, dt, button, config) {
              var params = datatable.ajax.params();
              params.visible = datatable.columns().visible().toArray();
              run_query(params, 'xml');
            }
          }]
        });
      }
    }
  }
});

// shake animation
function animateEl(element, animation, complete) {
    if (!element instanceof jQuery || !$(element).length || !animation) return null;

    if (element.data('animating')) {
        element.removeClass(element.data('animating')).data('animating', null);
        element.data('animationTimeout') && clearTimeout(element.data('animationTimeout'));
    }

    element.addClass('animated-' + animation).data('animating', 'animated-' + animation);
    element.data('animationTimeout', setTimeout((function() {
        element.removeClass(element.data('animating')).data('animating', null);
        complete && complete();
    }), 400));
}

// custom error handler instead of default datatable alert error
// this often happens when invalid datastore_search queries are returned
$.fn.dataTable.ext.errMode = 'none';
$('#dtprv').on('error.dt', function(e, settings, techNote, message) {
    console.log('DataTables error: ', message);

    // if error code 7, most probably an FTS query error. shake input
    if (techNote == 7) {
        const shake_element = $(":focus");
        animateEl(shake_element, 'shake');
    }
})