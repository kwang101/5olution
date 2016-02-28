var socket = io.connect('http://10.19.223.0:7984');

var audio = new Audio('../resources/burglar_alarm_bell_sounding.mp3');
audio.addEventListener('ended', function() {
    this.currentTime = 0;
    this.play();
}, false);
audio.play();
audio.muted = true;

function turnOffAudio() {
  audio.muted = true;
}

function turnOnAudio() {
  audio.muted = false;
}

socket.on('start_alarm', function(colour) {
  console.log('hi');
  turnOnAudio();
  console.log('bye');
  $('#itemRemovedModal').modal('show');
});

socket.on('stop_alarm', function(colour) {
  turnOffAudio();
  $('#itemRemovedModal').modal('hide');
});

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

function formatTime(hours, minutes) {
  var time = hours*60 + minutes;
  return time;
}

function formatStart(time) {
  var hours = parseInt(time.substring(0,2));
  var minutes = parseInt(time.substring(3,5));
  var time = hours*60 + minutes;
  return time;
}

function buildSchedule(days, startTime, duration, itemName) {
  schedule = {'days': {}};
  days.forEach(function(day) {
    schedule["days"][day] = {"start_time": startTime, "duration": duration, "item_name": itemName};
  });
  return schedule;
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
  $('#trs' + count).append($('<td><input type="checkbox" id="toggleId'+count+'"></td>'));
  var $toggle = $('#toggleId' + count);
  $toggle.on('click', function() {
    var dayArray = $('#daySelect' + count).val();
    var nameItem = $('#nameSelect' + count).val();
    var time = $('[value="09:30"]').val();
    var hours = parseInt($('#hours'+count).val());
    var minutes = parseInt($('#minutes'+count).val());
    var duration = formatTime(hours, minutes);
    var startTime = formatStart(time);
    var schedule = JSON.stringify(buildSchedule(dayArray, startTime, duration, nameItem));
    console.log(schedule);
    socket.emit('create_alarm', schedule);
    socket.emit('activate_alarm', schedule);
  });
  $('#trs' + count).append($('<td>').append($button));
});


