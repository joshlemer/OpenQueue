var app = angular.module('app', ['ngRoute', 'mgcrea.ngStrap', 'ngSanitize', 'ngCookies'])
	.config(function($interpolateProvider){
	    $interpolateProvider.startSymbol('[[').endSymbol(']]');
	})
	.config(['$routeProvider', function($routeProvider) {
	    $routeProvider
	    .when('/', {
	        controller: 'RoomListController',
	        controllerAs: 'list',
	        templateUrl: 'static/list.html'
	    })
	    .when('/rooms/:roomName', {
	        controller: 'RoomController',
	        controllerAs: 'room',
	        templateUrl: 'static/detail.html'
	    })
	    .when('/404', {
	        templateUrl: 'static/404.html'
	    })
	    .otherwise({
	        templateUrl: 'static/404.html'
	    });
	}])
    .controller('RoomController',['$http', '$routeParams','$scope', '$interval', '$rootScope', '$cookies', '$cookieStore', '$location',
     function($http, $routeParams, $scope, $interval, $rootScope, $cookies, $cookieStore, $location){
        var value = this;
        value.title = [];

        /**
        Really hacky, there's an issue where, when we update the data
        on the page with the loadRoom() function, all popovers close.
        This is terrible UX, so for now, don't auto-refresh unless no
        popovers are open.
        **/
        $rootScope.openPopovers = 0;

        $scope.loadRoom = function() {
            $http.get('/api/rooms/' + $routeParams.roomName).success(function(data){
                value.title=data;
                value.data = data;
                $scope.the_room = data;
                $rootScope.roomSlug = data.slug;
            })
            .error(function(data){
                $scope.isOn404=true;
                console.log($scope.isOn404);
            });
        };

        $rootScope.loadRoom = $scope.loadRoom;

        this.join = function(queue_id) {
            $http.post('/api/queues/' + queue_id + '/join/')
            .success( function(data) {
                $scope.loadRoom();
            });
        };
        this.openQueue = function(queue) {
            $rootScope.openQueue = queue;
        };

        //poll server every 30 seconds unless there are open popovers
        var promise = $interval( function() {
                if ($rootScope.openPopovers === 0){
                    $scope.loadRoom();
                }
            }, 30000);

        $scope.loadRoom();

        $scope.$on('$destroy', function() {
            if(angular.isDefined(promise)) {
                $interval.cancel(promise);
                promise = undefined;
            }
        });

    }])
    .controller('NewRoomController', ['$scope', '$http', function($scope, $http) {
        $scope.submit = function(newroom) {
            $http.post('/api/rooms/', {
                data: newroom
            }).success(function() {
                location.reload();
            });
        };
    }])
    .controller('NewQueueController', ['$scope', '$http', '$routeParams','$rootScope',
     function($scope, $http, $routeParams, $rootScope) {
        $scope.submit = function(newqueue) {
            $http.post('/api/rooms/' + $rootScope.roomSlug + '/queues/', {
                data: newqueue
            }).success(function() {
                $rootScope.loadRoom();
            });
        };
    }])
    .controller('RoomListController', ['$http', function($http){
        var value = this;
        $http.get('/api/rooms/').success(function(data){
            value.data = data;
        });
    }])
    .controller('ResourceController', ['$http', '$scope', function($http, $scope){

        $scope.queue_element = $scope.resource.current_queue_element;

    }])
    .controller('EditRoomController', ['$http', '$scope', '$rootScope', '$location', function($http, $scope, $rootScope, $location){
        $scope.newMember = function() {
            $rootScope.editingRoom.newMembers.push({})
        };
        $scope.deleteMember = function(member_id) {
            $scope.editingRoom.deletedMembers.push(member_id);
            $scope.editingRoom.members = $scope.editingRoom.members.filter(function(member) {
                return member._id !== member_id;
            });
        };
        $scope.openRoom = function() {
            $rootScope.editingRoom = angular.copy($scope.the_room);
            $rootScope.editingRoom.deletedMembers = [];
            $rootScope.editingRoom.newMembers = [];
        };

        $scope.delete = function(room) {
            $http.delete('/api/rooms/' + room.slug + '/')
            .success( function(data) {
                $location.path('/');
            });
        };

        $scope.submit = function(room) {
            $http.post('/api/rooms/' + room.slug + '/',{
                data: room
            })
            .success(function(){
                $rootScope.loadRoom();
            });
        };
    }])
    .controller('EditQueueController', ['$http', '$scope','$rootScope', function($http, $scope, $rootScope){

        $scope.newResource = function() {
            $rootScope.editingQueue.resources.push({isNew: true});
        };
        $scope.deleteResource = function(resource_id) {
            $scope.editingQueue.deletedResources.push(resource_id);
            $scope.editingQueue.resources = $scope.editingQueue.resources.filter(function(resource) {
                return resource._id !== resource_id;
            });
        };
        $scope.submit = function(queue) {
            $http.post('/api/rooms/' + $rootScope.roomSlug + '/queues/' + queue._id + '/',
            {
                data: queue
            })
            .success(function() {
                $scope.loadRoom();
            });
            console.log(queue);
        };

        $scope.delete = function(queue) {
            $http.delete('/api/rooms/' + $rootScope.roomSlug + '/queues/' + queue._id + '/')
            .success(function() {
                $scope.loadRoom();
            });
        };

        $scope.openQueue = function(queue) {
            $rootScope.editingQueue = angular.copy(queue);
            $rootScope.editingQueue.deletedResources = [];
        };
    }])
    .controller('QueueElementController', ['$http', '$scope', '$rootScope', function($http, $scope, $rootScope){

        $scope.openNewQueueElement = function() {
            var resources = [];
            for (var i = 0; i < $scope.queue.resources.length; i++){
                resources.push($scope.queue.resources[i]._id);
            }
            $rootScope.newQueueElement = {
                accepts: resources
            };
            $rootScope.openQueue = $scope.queue;
            console.log($rootScope.newQueueElement.accepts);
        };
        $scope.toggleSelection = function(resource_id) {
             var i = $rootScope.newQueueElement.accepts.indexOf(resource_id);

            if ( i >  -1 ){
                $rootScope.newQueueElement.accepts.splice(i, 1);
            } else {
                $rootScope.newQueueElement.accepts.push(resource_id);
            }
        }
        $scope.submitNewQueueElement = function(newQueueElement) {
            $http.post('/api/queues/' + $rootScope.openQueue._id + '/join/', {
                data: newQueueElement
            }).success(function(data) {
                $scope.loadRoom();
            });
        };
        $scope.delete = function() {
            $http.delete('/api/queues/' + $scope.queue._id + '/queue_elements/' + $scope.queue_element._id + '/').success( function(){
                $scope.loadRoom();
            });
        };

        $scope.save = function() {
            $http.post('/api/queues/' + $scope.queue._id + '/queue_elements/' + $scope.queue_element._id + '/',
                {
                    data: $scope.queue_element
                }
            ).success(function(data){
                $scope.loadRoom();
            });
        };

        //This ensures that data isn't fetched while popovers are open
        // ..which causes popovers to close
        this.popoverOpen = false;
        this.togglePopover = function() {
            if (this.popoverOpen){
                $rootScope.openPopovers--;
            } else {
                $rootScope.openPopovers++;
            }
            this.popoverOpen = !this.popoverOpen;
        }

    }])
    .directive("customPopover", ["$popover", "$compile", "$cookies",
    function($popover, $compile, $cookies) {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {
                var title = '';
                scope.isOpen = false;
                if (scope.queue_element){
                    title = scope.queue_element.user.email;
                }

                var myPopover = $popover(element, {
                    title: title,
                    contentTemplate: 'example.html',
                    html: true,
                    trigger: 'manual',
                    placement: 'right',
                    autoClose: false,
                    scope: scope
                });

                scope.togglePopover = function() {
                    scope.userId = $cookies.userId;
                    myPopover.toggle();
                }
            }
        }
    }]);
