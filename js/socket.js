var socket = io.connect('http://206.87.212.9:8083');

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
  turnOnAudio();
  $('#itemRemovedModal').modal('show');
});

socket.on('stop_alarm', function(colour) {
  turnOffAudio();
  $('#itemRemovedModal').modal('hide');
});

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
    return item;
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

$(".nav-tabs a").click(function(){
    event.preventDefault();
    $(this).tab('show');
});

