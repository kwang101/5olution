var socket = io.connect('http://206.87.212.9:8082');

var itemList = [];
var count = 0;

// Listen for initial server connection
socket.on('items', function(items) {
  var i = 0;
  if($('#objectTable').length == 1) {
    $('#objectTable').remove();
  }
  $('#objectHead').append($('<tbody id="objectTable"></tbody>'));
  JSON.parse(items).forEach(function(item) {
    i++;
    $('#objectTable').append('<tr id="tr'+i+'"></tr>');
    $('#tr' + i).append($('<td>').text(i));
    $('#tr' + i).append($('<td id="tdname'+i+'"></td>').text(item['name']));
    var $button = $('<button id="unregister'+i+'" class="btn btn-danger">Unregister</button>');
    $button.on('click', function() {
      unregisterItem(item.name);
    });
    $('#tr' + i).append($('<td>').append($button));
  });
});

function buildItem(itemName) {
  var item = {};
  item['item_name'] = itemName;
  var stringItem = JSON.stringify(item);
  return stringItem;
}

function unregisterItem(itemName) {
  socket.emit('unregister', buildItem(itemName));
}

$('#addButton').click(function() {
  var item = buildItem($('#objectName').val());
  socket.emit('register', item);
});

$(".nav-tabs a").click(function() {
    event.preventDefault();
    $(this).tab('show');
});

$('#scheduleTab').click(function() {
  socket.emit('get_items',{});
});

socket.on('itemList', function(items) {
  itemList = items;
});

$('#addSchedule').click(function() {
  console.log(itemList);
  count++;
  $('#scheduleHead').append($('<tbody id="scheduleTable"></tbody>'));
  $select = $('<td><select id="daySelect'+count+'" multiple="multiple"><option value="monday">Monday</option><option value="tuesday">Tuesday</option><option value="wednesday">Wednesday</option><option value="thursday">Thursday</option><option value="friday">Friday</option><option value="saturday">Saturday</option><option value="sunday">Sunday</option></select></td>');
  $('#scheduleTable').append('<tr id="trs'+count+'"></tr>');
  $('#trs' + count).append($select);
  $('#daySelect'+count).multiselect();
  $nameSelect = $('<td><form><div class="form-group margin-top-small"><select class="width-pix form-control" id="nameSelect'+count+'"></select></div></form></td>');
  $('#trs' + count).append($nameSelect);
  var i = 0;
  if(itemList.length > 0) {
    JSON.parse(itemList).forEach(function(item) {
      i++;
      $('#nameSelect'+count).append($('<option>').text(item.name));
    });
  }
  $('#trs' + count).append($('<td class="width-pix-big"><div class="margin-top-small input-group clockpicker"><input type="text" class="form-control" value="09:30"><span class="input-group-addon"><span class="glyphicon glyphicon-time"></span></span></div></td>'));
  $('#trs' + count).append($('<td class="width-small"><form><div class="form-group"><input placeholder="Hours" class="form-control" id="hours'+count+'"></input></div><div class="form-group"><input placeholder="Minutes" class="form-control" id="minutes'+count+'"></input></div></form></td>'));
  $('.clockpicker').clockpicker({
    donetext: 'Done'
  });
  var $button = $('<button id="remove'+count+'" class="btn btn-danger margin-top-small">Remove</button>');
  $button.on('click', function() {
    // removeAlarm(item.name);
  });
  $('#trs' + count).append($('<td>').append($button));
  $('#trs' + count).append($('<td><input type="checkbox" class="margin-top-small" id="toggleId'+count+'"name="toggleActivate" checked></td>'));
  $("[name='toggleActivate']").bootstrapSwitch();
});

