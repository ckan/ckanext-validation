(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory();
	else if(typeof define === 'function' && define.amd)
		define([], factory);
	else if(typeof exports === 'object')
		exports["goodtablesUI"] = factory();
	else
		root["goodtablesUI"] = factory();
})(this, function() {
return /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// identity function for calling harmony imports with the correct context
/******/ 	__webpack_require__.i = function(value) { return value; };
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, {
/******/ 				configurable: false,
/******/ 				enumerable: true,
/******/ 				get: getter
/******/ 			});
/******/ 		}
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "/dist/";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 13);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/* no static exports found */
/* all exports used */
/*!************************************************!*\
  !*** ./~/react-lite/dist/react-lite.common.js ***!
  \************************************************/
/***/ (function(module, exports, __webpack_require__) {

"use strict";
/*!
 * react-lite.js v0.15.33
 * (c) 2017 Jade Gu
 * Released under the MIT License.
 */


var HTML_KEY = 'dangerouslySetInnerHTML';
var SVGNamespaceURI = 'http://www.w3.org/2000/svg';
var COMPONENT_ID = 'liteid';
var VELEMENT = 2;
var VSTATELESS = 3;
var VCOMPONENT = 4;
var VCOMMENT = 5;
var ELEMENT_NODE_TYPE = 1;
var DOC_NODE_TYPE = 9;
var DOCUMENT_FRAGMENT_NODE_TYPE = 11;

/**
 * current stateful component's refs property
 * will attach to every vnode created by calling component.render method
 */
var refs = null;

function createVnode(vtype, type, props, key, ref) {
    var vnode = {
        vtype: vtype,
        type: type,
        props: props,
        refs: refs,
        key: key,
        ref: ref
    };
    if (vtype === VSTATELESS || vtype === VCOMPONENT) {
        vnode.uid = getUid();
    }
    return vnode;
}

function initVnode(vnode, parentContext, namespaceURI) {
    var vtype = vnode.vtype;

    var node = null;
    if (!vtype) {
        // init text
        node = document.createTextNode(vnode);
    } else if (vtype === VELEMENT) {
        // init element
        node = initVelem(vnode, parentContext, namespaceURI);
    } else if (vtype === VCOMPONENT) {
        // init stateful component
        node = initVcomponent(vnode, parentContext, namespaceURI);
    } else if (vtype === VSTATELESS) {
        // init stateless component
        node = initVstateless(vnode, parentContext, namespaceURI);
    } else if (vtype === VCOMMENT) {
        // init comment
        node = document.createComment('react-text: ' + (vnode.uid || getUid()));
    }
    return node;
}

function updateVnode(vnode, newVnode, node, parentContext) {
    var vtype = vnode.vtype;

    if (vtype === VCOMPONENT) {
        return updateVcomponent(vnode, newVnode, node, parentContext);
    }

    if (vtype === VSTATELESS) {
        return updateVstateless(vnode, newVnode, node, parentContext);
    }

    // ignore VCOMMENT and other vtypes
    if (vtype !== VELEMENT) {
        return node;
    }

    var oldHtml = vnode.props[HTML_KEY] && vnode.props[HTML_KEY].__html;
    if (oldHtml != null) {
        updateVelem(vnode, newVnode, node, parentContext);
        initVchildren(newVnode, node, parentContext);
    } else {
        updateVChildren(vnode, newVnode, node, parentContext);
        updateVelem(vnode, newVnode, node, parentContext);
    }
    return node;
}

function updateVChildren(vnode, newVnode, node, parentContext) {
    var patches = {
        removes: [],
        updates: [],
        creates: []
    };
    diffVchildren(patches, vnode, newVnode, node, parentContext);
    flatEach(patches.removes, applyDestroy);
    flatEach(patches.updates, applyUpdate);
    flatEach(patches.creates, applyCreate);
}

function applyUpdate(data) {
    if (!data) {
        return;
    }
    var vnode = data.vnode;
    var newNode = data.node;

    // update
    if (!data.shouldIgnore) {
        if (!vnode.vtype) {
            newNode.replaceData(0, newNode.length, data.newVnode);
        } else if (vnode.vtype === VELEMENT) {
            updateVelem(vnode, data.newVnode, newNode, data.parentContext);
        } else if (vnode.vtype === VSTATELESS) {
            newNode = updateVstateless(vnode, data.newVnode, newNode, data.parentContext);
        } else if (vnode.vtype === VCOMPONENT) {
            newNode = updateVcomponent(vnode, data.newVnode, newNode, data.parentContext);
        }
    }

    // re-order
    var currentNode = newNode.parentNode.childNodes[data.index];
    if (currentNode !== newNode) {
        newNode.parentNode.insertBefore(newNode, currentNode);
    }
    return newNode;
}

function applyDestroy(data) {
    destroyVnode(data.vnode, data.node);
    data.node.parentNode.removeChild(data.node);
}

function applyCreate(data) {
    var node = initVnode(data.vnode, data.parentContext, data.parentNode.namespaceURI);
    data.parentNode.insertBefore(node, data.parentNode.childNodes[data.index]);
}

/**
 * Only vnode which has props.children need to call destroy function
 * to check whether subTree has component that need to call lify-cycle method and release cache.
 */

function destroyVnode(vnode, node) {
    var vtype = vnode.vtype;

    if (vtype === VELEMENT) {
        // destroy element
        destroyVelem(vnode, node);
    } else if (vtype === VCOMPONENT) {
        // destroy state component
        destroyVcomponent(vnode, node);
    } else if (vtype === VSTATELESS) {
        // destroy stateless component
        destroyVstateless(vnode, node);
    }
}

function initVelem(velem, parentContext, namespaceURI) {
    var type = velem.type;
    var props = velem.props;

    var node = null;

    if (type === 'svg' || namespaceURI === SVGNamespaceURI) {
        node = document.createElementNS(SVGNamespaceURI, type);
        namespaceURI = SVGNamespaceURI;
    } else {
        node = document.createElement(type);
    }

    initVchildren(velem, node, parentContext);

    var isCustomComponent = type.indexOf('-') >= 0 || props.is != null;
    setProps(node, props, isCustomComponent);

    if (velem.ref != null) {
        addItem(pendingRefs, velem);
        addItem(pendingRefs, node);
    }

    return node;
}

function initVchildren(velem, node, parentContext) {
    var vchildren = node.vchildren = getFlattenChildren(velem);
    var namespaceURI = node.namespaceURI;
    for (var i = 0, len = vchildren.length; i < len; i++) {
        node.appendChild(initVnode(vchildren[i], parentContext, namespaceURI));
    }
}

function getFlattenChildren(vnode) {
    var children = vnode.props.children;

    var vchildren = [];
    if (isArr(children)) {
        flatEach(children, collectChild, vchildren);
    } else {
        collectChild(children, vchildren);
    }
    return vchildren;
}

function collectChild(child, children) {
    if (child != null && typeof child !== 'boolean') {
        if (!child.vtype) {
            // convert immutablejs data
            if (child.toJS) {
                child = child.toJS();
                if (isArr(child)) {
                    flatEach(child, collectChild, children);
                } else {
                    collectChild(child, children);
                }
                return;
            }
            child = '' + child;
        }
        children[children.length] = child;
    }
}

function diffVchildren(patches, vnode, newVnode, node, parentContext) {
    var childNodes = node.childNodes;
    var vchildren = node.vchildren;

    var newVchildren = node.vchildren = getFlattenChildren(newVnode);
    var vchildrenLen = vchildren.length;
    var newVchildrenLen = newVchildren.length;

    if (vchildrenLen === 0) {
        if (newVchildrenLen > 0) {
            for (var i = 0; i < newVchildrenLen; i++) {
                addItem(patches.creates, {
                    vnode: newVchildren[i],
                    parentNode: node,
                    parentContext: parentContext,
                    index: i
                });
            }
        }
        return;
    } else if (newVchildrenLen === 0) {
        for (var i = 0; i < vchildrenLen; i++) {
            addItem(patches.removes, {
                vnode: vchildren[i],
                node: childNodes[i]
            });
        }
        return;
    }

    var updates = Array(newVchildrenLen);
    var removes = null;
    var creates = null;

    // isEqual
    for (var i = 0; i < vchildrenLen; i++) {
        var _vnode = vchildren[i];
        for (var j = 0; j < newVchildrenLen; j++) {
            if (updates[j]) {
                continue;
            }
            var _newVnode = newVchildren[j];
            if (_vnode === _newVnode) {
                var shouldIgnore = true;
                if (parentContext) {
                    if (_vnode.vtype === VCOMPONENT || _vnode.vtype === VSTATELESS) {
                        if (_vnode.type.contextTypes) {
                            shouldIgnore = false;
                        }
                    }
                }
                updates[j] = {
                    shouldIgnore: shouldIgnore,
                    vnode: _vnode,
                    newVnode: _newVnode,
                    node: childNodes[i],
                    parentContext: parentContext,
                    index: j
                };
                vchildren[i] = null;
                break;
            }
        }
    }

    // isSimilar
    for (var i = 0; i < vchildrenLen; i++) {
        var _vnode2 = vchildren[i];
        if (_vnode2 === null) {
            continue;
        }
        var shouldRemove = true;
        for (var j = 0; j < newVchildrenLen; j++) {
            if (updates[j]) {
                continue;
            }
            var _newVnode2 = newVchildren[j];
            if (_newVnode2.type === _vnode2.type && _newVnode2.key === _vnode2.key && _newVnode2.refs === _vnode2.refs) {
                updates[j] = {
                    vnode: _vnode2,
                    newVnode: _newVnode2,
                    node: childNodes[i],
                    parentContext: parentContext,
                    index: j
                };
                shouldRemove = false;
                break;
            }
        }
        if (shouldRemove) {
            if (!removes) {
                removes = [];
            }
            addItem(removes, {
                vnode: _vnode2,
                node: childNodes[i]
            });
        }
    }

    for (var i = 0; i < newVchildrenLen; i++) {
        var item = updates[i];
        if (!item) {
            if (!creates) {
                creates = [];
            }
            addItem(creates, {
                vnode: newVchildren[i],
                parentNode: node,
                parentContext: parentContext,
                index: i
            });
        } else if (item.vnode.vtype === VELEMENT) {
            diffVchildren(patches, item.vnode, item.newVnode, item.node, item.parentContext);
        }
    }

    if (removes) {
        addItem(patches.removes, removes);
    }
    if (creates) {
        addItem(patches.creates, creates);
    }
    addItem(patches.updates, updates);
}

function updateVelem(velem, newVelem, node) {
    var isCustomComponent = velem.type.indexOf('-') >= 0 || velem.props.is != null;
    patchProps(node, velem.props, newVelem.props, isCustomComponent);
    if (velem.ref !== newVelem.ref) {
        detachRef(velem.refs, velem.ref, node);
        attachRef(newVelem.refs, newVelem.ref, node);
    }
    return node;
}

function destroyVelem(velem, node) {
    var props = velem.props;
    var vchildren = node.vchildren;
    var childNodes = node.childNodes;

    if (vchildren) {
        for (var i = 0, len = vchildren.length; i < len; i++) {
            destroyVnode(vchildren[i], childNodes[i]);
        }
    }
    detachRef(velem.refs, velem.ref, node);
    node.eventStore = node.vchildren = null;
}

function initVstateless(vstateless, parentContext, namespaceURI) {
    var vnode = renderVstateless(vstateless, parentContext);
    var node = initVnode(vnode, parentContext, namespaceURI);
    node.cache = node.cache || {};
    node.cache[vstateless.uid] = vnode;
    return node;
}

function updateVstateless(vstateless, newVstateless, node, parentContext) {
    var uid = vstateless.uid;
    var vnode = node.cache[uid];
    delete node.cache[uid];
    var newVnode = renderVstateless(newVstateless, parentContext);
    var newNode = compareTwoVnodes(vnode, newVnode, node, parentContext);
    newNode.cache = newNode.cache || {};
    newNode.cache[newVstateless.uid] = newVnode;
    if (newNode !== node) {
        syncCache(newNode.cache, node.cache, newNode);
    }
    return newNode;
}

function destroyVstateless(vstateless, node) {
    var uid = vstateless.uid;
    var vnode = node.cache[uid];
    delete node.cache[uid];
    destroyVnode(vnode, node);
}

function renderVstateless(vstateless, parentContext) {
    var factory = vstateless.type;
    var props = vstateless.props;

    var componentContext = getContextByTypes(parentContext, factory.contextTypes);
    var vnode = factory(props, componentContext);
    if (vnode && vnode.render) {
        vnode = vnode.render();
    }
    if (vnode === null || vnode === false) {
        vnode = createVnode(VCOMMENT);
    } else if (!vnode || !vnode.vtype) {
        throw new Error('@' + factory.name + '#render:You may have returned undefined, an array or some other invalid object');
    }
    return vnode;
}

function initVcomponent(vcomponent, parentContext, namespaceURI) {
    var Component = vcomponent.type;
    var props = vcomponent.props;
    var uid = vcomponent.uid;

    var componentContext = getContextByTypes(parentContext, Component.contextTypes);
    var component = new Component(props, componentContext);
    var updater = component.$updater;
    var cache = component.$cache;

    cache.parentContext = parentContext;
    updater.isPending = true;
    component.props = component.props || props;
    component.context = component.context || componentContext;
    if (component.componentWillMount) {
        component.componentWillMount();
        component.state = updater.getState();
    }
    var vnode = renderComponent(component);
    var node = initVnode(vnode, getChildContext(component, parentContext), namespaceURI);
    node.cache = node.cache || {};
    node.cache[uid] = component;
    cache.vnode = vnode;
    cache.node = node;
    cache.isMounted = true;
    addItem(pendingComponents, component);

    if (vcomponent.ref != null) {
        addItem(pendingRefs, vcomponent);
        addItem(pendingRefs, component);
    }

    return node;
}

function updateVcomponent(vcomponent, newVcomponent, node, parentContext) {
    var uid = vcomponent.uid;
    var component = node.cache[uid];
    var updater = component.$updater;
    var cache = component.$cache;
    var Component = newVcomponent.type;
    var nextProps = newVcomponent.props;

    var componentContext = getContextByTypes(parentContext, Component.contextTypes);
    delete node.cache[uid];
    node.cache[newVcomponent.uid] = component;
    cache.parentContext = parentContext;
    if (component.componentWillReceiveProps) {
        var needToggleIsPending = !updater.isPending;
        if (needToggleIsPending) updater.isPending = true;
        component.componentWillReceiveProps(nextProps, componentContext);
        if (needToggleIsPending) updater.isPending = false;
    }

    if (vcomponent.ref !== newVcomponent.ref) {
        detachRef(vcomponent.refs, vcomponent.ref, component);
        attachRef(newVcomponent.refs, newVcomponent.ref, component);
    }

    updater.emitUpdate(nextProps, componentContext);

    return cache.node;
}

function destroyVcomponent(vcomponent, node) {
    var uid = vcomponent.uid;
    var component = node.cache[uid];
    var cache = component.$cache;
    delete node.cache[uid];
    detachRef(vcomponent.refs, vcomponent.ref, component);
    component.setState = component.forceUpdate = noop;
    if (component.componentWillUnmount) {
        component.componentWillUnmount();
    }
    destroyVnode(cache.vnode, node);
    delete component.setState;
    cache.isMounted = false;
    cache.node = cache.parentContext = cache.vnode = component.refs = component.context = null;
}

function getContextByTypes(curContext, contextTypes) {
    var context = {};
    if (!contextTypes || !curContext) {
        return context;
    }
    for (var key in contextTypes) {
        if (contextTypes.hasOwnProperty(key)) {
            context[key] = curContext[key];
        }
    }
    return context;
}

function renderComponent(component, parentContext) {
    refs = component.refs;
    var vnode = component.render();
    if (vnode === null || vnode === false) {
        vnode = createVnode(VCOMMENT);
    } else if (!vnode || !vnode.vtype) {
        throw new Error('@' + component.constructor.name + '#render:You may have returned undefined, an array or some other invalid object');
    }
    refs = null;
    return vnode;
}

function getChildContext(component, parentContext) {
    if (component.getChildContext) {
        var curContext = component.getChildContext();
        if (curContext) {
            parentContext = extend(extend({}, parentContext), curContext);
        }
    }
    return parentContext;
}

var pendingComponents = [];
function clearPendingComponents() {
    var len = pendingComponents.length;
    if (!len) {
        return;
    }
    var components = pendingComponents;
    pendingComponents = [];
    var i = -1;
    while (len--) {
        var component = components[++i];
        var updater = component.$updater;
        if (component.componentDidMount) {
            component.componentDidMount();
        }
        updater.isPending = false;
        updater.emitUpdate();
    }
}

var pendingRefs = [];
function clearPendingRefs() {
    var len = pendingRefs.length;
    if (!len) {
        return;
    }
    var list = pendingRefs;
    pendingRefs = [];
    for (var i = 0; i < len; i += 2) {
        var vnode = list[i];
        var refValue = list[i + 1];
        attachRef(vnode.refs, vnode.ref, refValue);
    }
}

function clearPending() {
    clearPendingRefs();
    clearPendingComponents();
}

function compareTwoVnodes(vnode, newVnode, node, parentContext) {
    var newNode = node;
    if (newVnode == null) {
        // remove
        destroyVnode(vnode, node);
        node.parentNode.removeChild(node);
    } else if (vnode.type !== newVnode.type || vnode.key !== newVnode.key) {
        // replace
        destroyVnode(vnode, node);
        newNode = initVnode(newVnode, parentContext, node.namespaceURI);
        node.parentNode.replaceChild(newNode, node);
    } else if (vnode !== newVnode || parentContext) {
        // same type and same key -> update
        newNode = updateVnode(vnode, newVnode, node, parentContext);
    }
    return newNode;
}

function getDOMNode() {
    return this;
}

function attachRef(refs, refKey, refValue) {
    if (refKey == null || !refValue) {
        return;
    }
    if (refValue.nodeName && !refValue.getDOMNode) {
        // support react v0.13 style: this.refs.myInput.getDOMNode()
        refValue.getDOMNode = getDOMNode;
    }
    if (isFn(refKey)) {
        refKey(refValue);
    } else if (refs) {
        refs[refKey] = refValue;
    }
}

function detachRef(refs, refKey, refValue) {
    if (refKey == null) {
        return;
    }
    if (isFn(refKey)) {
        refKey(null);
    } else if (refs && refs[refKey] === refValue) {
        delete refs[refKey];
    }
}

function syncCache(cache, oldCache, node) {
    for (var key in oldCache) {
        if (!oldCache.hasOwnProperty(key)) {
            continue;
        }
        var value = oldCache[key];
        cache[key] = value;

        // is component, update component.$cache.node
        if (value.forceUpdate) {
            value.$cache.node = node;
        }
    }
}

var updateQueue = {
	updaters: [],
	isPending: false,
	add: function add(updater) {
		addItem(this.updaters, updater);
	},
	batchUpdate: function batchUpdate() {
		if (this.isPending) {
			return;
		}
		this.isPending = true;
		/*
   each updater.update may add new updater to updateQueue
   clear them with a loop
   event bubbles from bottom-level to top-level
   reverse the updater order can merge some props and state and reduce the refresh times
   see Updater.update method below to know why
  */
		var updaters = this.updaters;

		var updater = undefined;
		while (updater = updaters.pop()) {
			updater.updateComponent();
		}
		this.isPending = false;
	}
};

function Updater(instance) {
	this.instance = instance;
	this.pendingStates = [];
	this.pendingCallbacks = [];
	this.isPending = false;
	this.nextProps = this.nextContext = null;
	this.clearCallbacks = this.clearCallbacks.bind(this);
}

Updater.prototype = {
	emitUpdate: function emitUpdate(nextProps, nextContext) {
		this.nextProps = nextProps;
		this.nextContext = nextContext;
		// receive nextProps!! should update immediately
		nextProps || !updateQueue.isPending ? this.updateComponent() : updateQueue.add(this);
	},
	updateComponent: function updateComponent() {
		var instance = this.instance;
		var pendingStates = this.pendingStates;
		var nextProps = this.nextProps;
		var nextContext = this.nextContext;

		if (nextProps || pendingStates.length > 0) {
			nextProps = nextProps || instance.props;
			nextContext = nextContext || instance.context;
			this.nextProps = this.nextContext = null;
			// merge the nextProps and nextState and update by one time
			shouldUpdate(instance, nextProps, this.getState(), nextContext, this.clearCallbacks);
		}
	},
	addState: function addState(nextState) {
		if (nextState) {
			addItem(this.pendingStates, nextState);
			if (!this.isPending) {
				this.emitUpdate();
			}
		}
	},
	replaceState: function replaceState(nextState) {
		var pendingStates = this.pendingStates;

		pendingStates.pop();
		// push special params to point out should replace state
		addItem(pendingStates, [nextState]);
	},
	getState: function getState() {
		var instance = this.instance;
		var pendingStates = this.pendingStates;
		var state = instance.state;
		var props = instance.props;

		if (pendingStates.length) {
			state = extend({}, state);
			pendingStates.forEach(function (nextState) {
				var isReplace = isArr(nextState);
				if (isReplace) {
					nextState = nextState[0];
				}
				if (isFn(nextState)) {
					nextState = nextState.call(instance, state, props);
				}
				// replace state
				if (isReplace) {
					state = extend({}, nextState);
				} else {
					extend(state, nextState);
				}
			});
			pendingStates.length = 0;
		}
		return state;
	},
	clearCallbacks: function clearCallbacks() {
		var pendingCallbacks = this.pendingCallbacks;
		var instance = this.instance;

		if (pendingCallbacks.length > 0) {
			this.pendingCallbacks = [];
			pendingCallbacks.forEach(function (callback) {
				return callback.call(instance);
			});
		}
	},
	addCallback: function addCallback(callback) {
		if (isFn(callback)) {
			addItem(this.pendingCallbacks, callback);
		}
	}
};
function Component(props, context) {
	this.$updater = new Updater(this);
	this.$cache = { isMounted: false };
	this.props = props;
	this.state = {};
	this.refs = {};
	this.context = context;
}

var ReactComponentSymbol = {};

Component.prototype = {
	constructor: Component,
	isReactComponent: ReactComponentSymbol,
	// getChildContext: _.noop,
	// componentWillUpdate: _.noop,
	// componentDidUpdate: _.noop,
	// componentWillReceiveProps: _.noop,
	// componentWillMount: _.noop,
	// componentDidMount: _.noop,
	// componentWillUnmount: _.noop,
	// shouldComponentUpdate(nextProps, nextState) {
	// 	return true
	// },
	forceUpdate: function forceUpdate(callback) {
		var $updater = this.$updater;
		var $cache = this.$cache;
		var props = this.props;
		var state = this.state;
		var context = this.context;

		if (!$cache.isMounted) {
			return;
		}
		// if updater is pending, add state to trigger nexttick update
		if ($updater.isPending) {
			$updater.addState(state);
			return;
		}
		var nextProps = $cache.props || props;
		var nextState = $cache.state || state;
		var nextContext = $cache.context || context;
		var parentContext = $cache.parentContext;
		var node = $cache.node;
		var vnode = $cache.vnode;
		$cache.props = $cache.state = $cache.context = null;
		$updater.isPending = true;
		if (this.componentWillUpdate) {
			this.componentWillUpdate(nextProps, nextState, nextContext);
		}
		this.state = nextState;
		this.props = nextProps;
		this.context = nextContext;
		var newVnode = renderComponent(this);
		var newNode = compareTwoVnodes(vnode, newVnode, node, getChildContext(this, parentContext));
		if (newNode !== node) {
			newNode.cache = newNode.cache || {};
			syncCache(newNode.cache, node.cache, newNode);
		}
		$cache.vnode = newVnode;
		$cache.node = newNode;
		clearPending();
		if (this.componentDidUpdate) {
			this.componentDidUpdate(props, state, context);
		}
		if (callback) {
			callback.call(this);
		}
		$updater.isPending = false;
		$updater.emitUpdate();
	},
	setState: function setState(nextState, callback) {
		var $updater = this.$updater;

		$updater.addCallback(callback);
		$updater.addState(nextState);
	},
	replaceState: function replaceState(nextState, callback) {
		var $updater = this.$updater;

		$updater.addCallback(callback);
		$updater.replaceState(nextState);
	},
	getDOMNode: function getDOMNode() {
		var node = this.$cache.node;
		return node && node.nodeName === '#comment' ? null : node;
	},
	isMounted: function isMounted() {
		return this.$cache.isMounted;
	}
};

function shouldUpdate(component, nextProps, nextState, nextContext, callback) {
	var shouldComponentUpdate = true;
	if (component.shouldComponentUpdate) {
		shouldComponentUpdate = component.shouldComponentUpdate(nextProps, nextState, nextContext);
	}
	if (shouldComponentUpdate === false) {
		component.props = nextProps;
		component.state = nextState;
		component.context = nextContext || {};
		return;
	}
	var cache = component.$cache;
	cache.props = nextProps;
	cache.state = nextState;
	cache.context = nextContext || {};
	component.forceUpdate(callback);
}

// event config
var unbubbleEvents = {
    /**
     * should not bind mousemove in document scope
     * even though mousemove event can bubble
     */
    onmousemove: 1,
    ontouchmove: 1,
    onmouseleave: 1,
    onmouseenter: 1,
    onload: 1,
    onunload: 1,
    onscroll: 1,
    onfocus: 1,
    onblur: 1,
    onrowexit: 1,
    onbeforeunload: 1,
    onstop: 1,
    ondragdrop: 1,
    ondragenter: 1,
    ondragexit: 1,
    ondraggesture: 1,
    ondragover: 1,
    oncontextmenu: 1,
    onerror: 1
};

function getEventName(key) {
    if (key === 'onDoubleClick') {
        key = 'ondblclick';
    } else if (key === 'onTouchTap') {
        key = 'onclick';
    }

    return key.toLowerCase();
}

// Mobile Safari does not fire properly bubble click events on
// non-interactive elements, which means delegated click listeners do not
// fire. The workaround for this bug involves attaching an empty click
// listener on the target node.
var inMobile = ('ontouchstart' in document);
var emptyFunction = function emptyFunction() {};
var ON_CLICK_KEY = 'onclick';

var eventTypes = {};

function addEvent(elem, eventType, listener) {
    eventType = getEventName(eventType);

    var eventStore = elem.eventStore || (elem.eventStore = {});
    eventStore[eventType] = listener;

    if (unbubbleEvents[eventType] === 1) {
        elem[eventType] = dispatchUnbubbleEvent;
        return;
    } else if (!eventTypes[eventType]) {
        // onclick -> click
        document.addEventListener(eventType.substr(2), dispatchEvent, false);
        eventTypes[eventType] = true;
    }

    if (inMobile && eventType === ON_CLICK_KEY) {
        elem.addEventListener('click', emptyFunction, false);
        return;
    }

    var nodeName = elem.nodeName;

    if (eventType === 'onchange') {
        addEvent(elem, 'oninput', listener);
    }
}

function removeEvent(elem, eventType) {
    eventType = getEventName(eventType);

    var eventStore = elem.eventStore || (elem.eventStore = {});
    delete eventStore[eventType];

    if (unbubbleEvents[eventType] === 1) {
        elem[eventType] = null;
        return;
    } else if (inMobile && eventType === ON_CLICK_KEY) {
        elem.removeEventListener('click', emptyFunction, false);
        return;
    }

    var nodeName = elem.nodeName;

    if (eventType === 'onchange') {
        delete eventStore['oninput'];
    }
}

function dispatchEvent(event) {
    var target = event.target;
    var type = event.type;

    var eventType = 'on' + type;
    var syntheticEvent = undefined;

    updateQueue.isPending = true;
    while (target) {
        var _target = target;
        var eventStore = _target.eventStore;

        var listener = eventStore && eventStore[eventType];
        if (!listener) {
            target = target.parentNode;
            continue;
        }
        if (!syntheticEvent) {
            syntheticEvent = createSyntheticEvent(event);
        }
        syntheticEvent.currentTarget = target;
        listener.call(target, syntheticEvent);
        if (syntheticEvent.$cancelBubble) {
            break;
        }
        target = target.parentNode;
    }
    updateQueue.isPending = false;
    updateQueue.batchUpdate();
}

function dispatchUnbubbleEvent(event) {
    var target = event.currentTarget || event.target;
    var eventType = 'on' + event.type;
    var syntheticEvent = createSyntheticEvent(event);

    syntheticEvent.currentTarget = target;
    updateQueue.isPending = true;

    var eventStore = target.eventStore;

    var listener = eventStore && eventStore[eventType];
    if (listener) {
        listener.call(target, syntheticEvent);
    }

    updateQueue.isPending = false;
    updateQueue.batchUpdate();
}

function createSyntheticEvent(nativeEvent) {
    var syntheticEvent = {};
    var cancelBubble = function cancelBubble() {
        return syntheticEvent.$cancelBubble = true;
    };
    syntheticEvent.nativeEvent = nativeEvent;
    syntheticEvent.persist = noop;
    for (var key in nativeEvent) {
        if (typeof nativeEvent[key] !== 'function') {
            syntheticEvent[key] = nativeEvent[key];
        } else if (key === 'stopPropagation' || key === 'stopImmediatePropagation') {
            syntheticEvent[key] = cancelBubble;
        } else {
            syntheticEvent[key] = nativeEvent[key].bind(nativeEvent);
        }
    }
    return syntheticEvent;
}

function setStyle(elemStyle, styles) {
    for (var styleName in styles) {
        if (styles.hasOwnProperty(styleName)) {
            setStyleValue(elemStyle, styleName, styles[styleName]);
        }
    }
}

function removeStyle(elemStyle, styles) {
    for (var styleName in styles) {
        if (styles.hasOwnProperty(styleName)) {
            elemStyle[styleName] = '';
        }
    }
}

function patchStyle(elemStyle, style, newStyle) {
    if (style === newStyle) {
        return;
    }
    if (!newStyle && style) {
        removeStyle(elemStyle, style);
        return;
    } else if (newStyle && !style) {
        setStyle(elemStyle, newStyle);
        return;
    }

    for (var key in style) {
        if (newStyle.hasOwnProperty(key)) {
            if (newStyle[key] !== style[key]) {
                setStyleValue(elemStyle, key, newStyle[key]);
            }
        } else {
            elemStyle[key] = '';
        }
    }
    for (var key in newStyle) {
        if (!style.hasOwnProperty(key)) {
            setStyleValue(elemStyle, key, newStyle[key]);
        }
    }
}

/**
 * CSS properties which accept numbers but are not in units of "px".
 */
var isUnitlessNumber = {
    animationIterationCount: 1,
    borderImageOutset: 1,
    borderImageSlice: 1,
    borderImageWidth: 1,
    boxFlex: 1,
    boxFlexGroup: 1,
    boxOrdinalGroup: 1,
    columnCount: 1,
    flex: 1,
    flexGrow: 1,
    flexPositive: 1,
    flexShrink: 1,
    flexNegative: 1,
    flexOrder: 1,
    gridRow: 1,
    gridColumn: 1,
    fontWeight: 1,
    lineClamp: 1,
    lineHeight: 1,
    opacity: 1,
    order: 1,
    orphans: 1,
    tabSize: 1,
    widows: 1,
    zIndex: 1,
    zoom: 1,

    // SVG-related properties
    fillOpacity: 1,
    floodOpacity: 1,
    stopOpacity: 1,
    strokeDasharray: 1,
    strokeDashoffset: 1,
    strokeMiterlimit: 1,
    strokeOpacity: 1,
    strokeWidth: 1
};

function prefixKey(prefix, key) {
    return prefix + key.charAt(0).toUpperCase() + key.substring(1);
}

var prefixes = ['Webkit', 'ms', 'Moz', 'O'];

Object.keys(isUnitlessNumber).forEach(function (prop) {
    prefixes.forEach(function (prefix) {
        isUnitlessNumber[prefixKey(prefix, prop)] = 1;
    });
});

var RE_NUMBER = /^-?\d+(\.\d+)?$/;
function setStyleValue(elemStyle, styleName, styleValue) {

    if (!isUnitlessNumber[styleName] && RE_NUMBER.test(styleValue)) {
        elemStyle[styleName] = styleValue + 'px';
        return;
    }

    if (styleName === 'float') {
        styleName = 'cssFloat';
    }

    if (styleValue == null || typeof styleValue === 'boolean') {
        styleValue = '';
    }

    elemStyle[styleName] = styleValue;
}

var ATTRIBUTE_NAME_START_CHAR = ':A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD';
var ATTRIBUTE_NAME_CHAR = ATTRIBUTE_NAME_START_CHAR + '\\-.0-9\\uB7\\u0300-\\u036F\\u203F-\\u2040';

var VALID_ATTRIBUTE_NAME_REGEX = new RegExp('^[' + ATTRIBUTE_NAME_START_CHAR + '][' + ATTRIBUTE_NAME_CHAR + ']*$');

var isCustomAttribute = RegExp.prototype.test.bind(new RegExp('^(data|aria)-[' + ATTRIBUTE_NAME_CHAR + ']*$'));
// will merge some data in properties below
var properties = {};

/**
 * Mapping from normalized, camelcased property names to a configuration that
 * specifies how the associated DOM property should be accessed or rendered.
 */
var MUST_USE_PROPERTY = 0x1;
var HAS_BOOLEAN_VALUE = 0x4;
var HAS_NUMERIC_VALUE = 0x8;
var HAS_POSITIVE_NUMERIC_VALUE = 0x10 | 0x8;
var HAS_OVERLOADED_BOOLEAN_VALUE = 0x20;

// html config
var HTMLDOMPropertyConfig = {
    props: {
        /**
         * Standard Properties
         */
        accept: 0,
        acceptCharset: 0,
        accessKey: 0,
        action: 0,
        allowFullScreen: HAS_BOOLEAN_VALUE,
        allowTransparency: 0,
        alt: 0,
        async: HAS_BOOLEAN_VALUE,
        autoComplete: 0,
        autoFocus: HAS_BOOLEAN_VALUE,
        autoPlay: HAS_BOOLEAN_VALUE,
        capture: HAS_BOOLEAN_VALUE,
        cellPadding: 0,
        cellSpacing: 0,
        charSet: 0,
        challenge: 0,
        checked: MUST_USE_PROPERTY | HAS_BOOLEAN_VALUE,
        cite: 0,
        classID: 0,
        className: 0,
        cols: HAS_POSITIVE_NUMERIC_VALUE,
        colSpan: 0,
        content: 0,
        contentEditable: 0,
        contextMenu: 0,
        controls: HAS_BOOLEAN_VALUE,
        coords: 0,
        crossOrigin: 0,
        data: 0, // For `<object />` acts as `src`.
        dateTime: 0,
        'default': HAS_BOOLEAN_VALUE,
        // not in regular react, they did it in other way
        defaultValue: MUST_USE_PROPERTY,
        // not in regular react, they did it in other way
        defaultChecked: MUST_USE_PROPERTY | HAS_BOOLEAN_VALUE,
        defer: HAS_BOOLEAN_VALUE,
        dir: 0,
        disabled: HAS_BOOLEAN_VALUE,
        download: HAS_OVERLOADED_BOOLEAN_VALUE,
        draggable: 0,
        encType: 0,
        form: 0,
        formAction: 0,
        formEncType: 0,
        formMethod: 0,
        formNoValidate: HAS_BOOLEAN_VALUE,
        formTarget: 0,
        frameBorder: 0,
        headers: 0,
        height: 0,
        hidden: HAS_BOOLEAN_VALUE,
        high: 0,
        href: 0,
        hrefLang: 0,
        htmlFor: 0,
        httpEquiv: 0,
        icon: 0,
        id: 0,
        inputMode: 0,
        integrity: 0,
        is: 0,
        keyParams: 0,
        keyType: 0,
        kind: 0,
        label: 0,
        lang: 0,
        list: 0,
        loop: HAS_BOOLEAN_VALUE,
        low: 0,
        manifest: 0,
        marginHeight: 0,
        marginWidth: 0,
        max: 0,
        maxLength: 0,
        media: 0,
        mediaGroup: 0,
        method: 0,
        min: 0,
        minLength: 0,
        // Caution; `option.selected` is not updated if `select.multiple` is
        // disabled with `removeAttribute`.
        multiple: MUST_USE_PROPERTY | HAS_BOOLEAN_VALUE,
        muted: MUST_USE_PROPERTY | HAS_BOOLEAN_VALUE,
        name: 0,
        nonce: 0,
        noValidate: HAS_BOOLEAN_VALUE,
        open: HAS_BOOLEAN_VALUE,
        optimum: 0,
        pattern: 0,
        placeholder: 0,
        poster: 0,
        preload: 0,
        profile: 0,
        radioGroup: 0,
        readOnly: HAS_BOOLEAN_VALUE,
        referrerPolicy: 0,
        rel: 0,
        required: HAS_BOOLEAN_VALUE,
        reversed: HAS_BOOLEAN_VALUE,
        role: 0,
        rows: HAS_POSITIVE_NUMERIC_VALUE,
        rowSpan: HAS_NUMERIC_VALUE,
        sandbox: 0,
        scope: 0,
        scoped: HAS_BOOLEAN_VALUE,
        scrolling: 0,
        seamless: HAS_BOOLEAN_VALUE,
        selected: MUST_USE_PROPERTY | HAS_BOOLEAN_VALUE,
        shape: 0,
        size: HAS_POSITIVE_NUMERIC_VALUE,
        sizes: 0,
        span: HAS_POSITIVE_NUMERIC_VALUE,
        spellCheck: 0,
        src: 0,
        srcDoc: 0,
        srcLang: 0,
        srcSet: 0,
        start: HAS_NUMERIC_VALUE,
        step: 0,
        style: 0,
        summary: 0,
        tabIndex: 0,
        target: 0,
        title: 0,
        // Setting .type throws on non-<input> tags
        type: 0,
        useMap: 0,
        value: MUST_USE_PROPERTY,
        width: 0,
        wmode: 0,
        wrap: 0,

        /**
         * RDFa Properties
         */
        about: 0,
        datatype: 0,
        inlist: 0,
        prefix: 0,
        // property is also supported for OpenGraph in meta tags.
        property: 0,
        resource: 0,
        'typeof': 0,
        vocab: 0,

        /**
         * Non-standard Properties
         */
        // autoCapitalize and autoCorrect are supported in Mobile Safari for
        // keyboard hints.
        autoCapitalize: 0,
        autoCorrect: 0,
        // autoSave allows WebKit/Blink to persist values of input fields on page reloads
        autoSave: 0,
        // color is for Safari mask-icon link
        color: 0,
        // itemProp, itemScope, itemType are for
        // Microdata support. See http://schema.org/docs/gs.html
        itemProp: 0,
        itemScope: HAS_BOOLEAN_VALUE,
        itemType: 0,
        // itemID and itemRef are for Microdata support as well but
        // only specified in the WHATWG spec document. See
        // https://html.spec.whatwg.org/multipage/microdata.html#microdata-dom-api
        itemID: 0,
        itemRef: 0,
        // results show looking glass icon and recent searches on input
        // search fields in WebKit/Blink
        results: 0,
        // IE-only attribute that specifies security restrictions on an iframe
        // as an alternative to the sandbox attribute on IE<10
        security: 0,
        // IE-only attribute that controls focus behavior
        unselectable: 0
    },
    attrNS: {},
    domAttrs: {
        acceptCharset: 'accept-charset',
        className: 'class',
        htmlFor: 'for',
        httpEquiv: 'http-equiv'
    },
    domProps: {}
};

// svg config
var xlink = 'http://www.w3.org/1999/xlink';
var xml = 'http://www.w3.org/XML/1998/namespace';

// We use attributes for everything SVG so let's avoid some duplication and run
// code instead.
// The following are all specified in the HTML config already so we exclude here.
// - class (as className)
// - color
// - height
// - id
// - lang
// - max
// - media
// - method
// - min
// - name
// - style
// - target
// - type
// - width
var ATTRS = {
    accentHeight: 'accent-height',
    accumulate: 0,
    additive: 0,
    alignmentBaseline: 'alignment-baseline',
    allowReorder: 'allowReorder',
    alphabetic: 0,
    amplitude: 0,
    arabicForm: 'arabic-form',
    ascent: 0,
    attributeName: 'attributeName',
    attributeType: 'attributeType',
    autoReverse: 'autoReverse',
    azimuth: 0,
    baseFrequency: 'baseFrequency',
    baseProfile: 'baseProfile',
    baselineShift: 'baseline-shift',
    bbox: 0,
    begin: 0,
    bias: 0,
    by: 0,
    calcMode: 'calcMode',
    capHeight: 'cap-height',
    clip: 0,
    clipPath: 'clip-path',
    clipRule: 'clip-rule',
    clipPathUnits: 'clipPathUnits',
    colorInterpolation: 'color-interpolation',
    colorInterpolationFilters: 'color-interpolation-filters',
    colorProfile: 'color-profile',
    colorRendering: 'color-rendering',
    contentScriptType: 'contentScriptType',
    contentStyleType: 'contentStyleType',
    cursor: 0,
    cx: 0,
    cy: 0,
    d: 0,
    decelerate: 0,
    descent: 0,
    diffuseConstant: 'diffuseConstant',
    direction: 0,
    display: 0,
    divisor: 0,
    dominantBaseline: 'dominant-baseline',
    dur: 0,
    dx: 0,
    dy: 0,
    edgeMode: 'edgeMode',
    elevation: 0,
    enableBackground: 'enable-background',
    end: 0,
    exponent: 0,
    externalResourcesRequired: 'externalResourcesRequired',
    fill: 0,
    fillOpacity: 'fill-opacity',
    fillRule: 'fill-rule',
    filter: 0,
    filterRes: 'filterRes',
    filterUnits: 'filterUnits',
    floodColor: 'flood-color',
    floodOpacity: 'flood-opacity',
    focusable: 0,
    fontFamily: 'font-family',
    fontSize: 'font-size',
    fontSizeAdjust: 'font-size-adjust',
    fontStretch: 'font-stretch',
    fontStyle: 'font-style',
    fontVariant: 'font-variant',
    fontWeight: 'font-weight',
    format: 0,
    from: 0,
    fx: 0,
    fy: 0,
    g1: 0,
    g2: 0,
    glyphName: 'glyph-name',
    glyphOrientationHorizontal: 'glyph-orientation-horizontal',
    glyphOrientationVertical: 'glyph-orientation-vertical',
    glyphRef: 'glyphRef',
    gradientTransform: 'gradientTransform',
    gradientUnits: 'gradientUnits',
    hanging: 0,
    horizAdvX: 'horiz-adv-x',
    horizOriginX: 'horiz-origin-x',
    ideographic: 0,
    imageRendering: 'image-rendering',
    'in': 0,
    in2: 0,
    intercept: 0,
    k: 0,
    k1: 0,
    k2: 0,
    k3: 0,
    k4: 0,
    kernelMatrix: 'kernelMatrix',
    kernelUnitLength: 'kernelUnitLength',
    kerning: 0,
    keyPoints: 'keyPoints',
    keySplines: 'keySplines',
    keyTimes: 'keyTimes',
    lengthAdjust: 'lengthAdjust',
    letterSpacing: 'letter-spacing',
    lightingColor: 'lighting-color',
    limitingConeAngle: 'limitingConeAngle',
    local: 0,
    markerEnd: 'marker-end',
    markerMid: 'marker-mid',
    markerStart: 'marker-start',
    markerHeight: 'markerHeight',
    markerUnits: 'markerUnits',
    markerWidth: 'markerWidth',
    mask: 0,
    maskContentUnits: 'maskContentUnits',
    maskUnits: 'maskUnits',
    mathematical: 0,
    mode: 0,
    numOctaves: 'numOctaves',
    offset: 0,
    opacity: 0,
    operator: 0,
    order: 0,
    orient: 0,
    orientation: 0,
    origin: 0,
    overflow: 0,
    overlinePosition: 'overline-position',
    overlineThickness: 'overline-thickness',
    paintOrder: 'paint-order',
    panose1: 'panose-1',
    pathLength: 'pathLength',
    patternContentUnits: 'patternContentUnits',
    patternTransform: 'patternTransform',
    patternUnits: 'patternUnits',
    pointerEvents: 'pointer-events',
    points: 0,
    pointsAtX: 'pointsAtX',
    pointsAtY: 'pointsAtY',
    pointsAtZ: 'pointsAtZ',
    preserveAlpha: 'preserveAlpha',
    preserveAspectRatio: 'preserveAspectRatio',
    primitiveUnits: 'primitiveUnits',
    r: 0,
    radius: 0,
    refX: 'refX',
    refY: 'refY',
    renderingIntent: 'rendering-intent',
    repeatCount: 'repeatCount',
    repeatDur: 'repeatDur',
    requiredExtensions: 'requiredExtensions',
    requiredFeatures: 'requiredFeatures',
    restart: 0,
    result: 0,
    rotate: 0,
    rx: 0,
    ry: 0,
    scale: 0,
    seed: 0,
    shapeRendering: 'shape-rendering',
    slope: 0,
    spacing: 0,
    specularConstant: 'specularConstant',
    specularExponent: 'specularExponent',
    speed: 0,
    spreadMethod: 'spreadMethod',
    startOffset: 'startOffset',
    stdDeviation: 'stdDeviation',
    stemh: 0,
    stemv: 0,
    stitchTiles: 'stitchTiles',
    stopColor: 'stop-color',
    stopOpacity: 'stop-opacity',
    strikethroughPosition: 'strikethrough-position',
    strikethroughThickness: 'strikethrough-thickness',
    string: 0,
    stroke: 0,
    strokeDasharray: 'stroke-dasharray',
    strokeDashoffset: 'stroke-dashoffset',
    strokeLinecap: 'stroke-linecap',
    strokeLinejoin: 'stroke-linejoin',
    strokeMiterlimit: 'stroke-miterlimit',
    strokeOpacity: 'stroke-opacity',
    strokeWidth: 'stroke-width',
    surfaceScale: 'surfaceScale',
    systemLanguage: 'systemLanguage',
    tableValues: 'tableValues',
    targetX: 'targetX',
    targetY: 'targetY',
    textAnchor: 'text-anchor',
    textDecoration: 'text-decoration',
    textRendering: 'text-rendering',
    textLength: 'textLength',
    to: 0,
    transform: 0,
    u1: 0,
    u2: 0,
    underlinePosition: 'underline-position',
    underlineThickness: 'underline-thickness',
    unicode: 0,
    unicodeBidi: 'unicode-bidi',
    unicodeRange: 'unicode-range',
    unitsPerEm: 'units-per-em',
    vAlphabetic: 'v-alphabetic',
    vHanging: 'v-hanging',
    vIdeographic: 'v-ideographic',
    vMathematical: 'v-mathematical',
    values: 0,
    vectorEffect: 'vector-effect',
    version: 0,
    vertAdvY: 'vert-adv-y',
    vertOriginX: 'vert-origin-x',
    vertOriginY: 'vert-origin-y',
    viewBox: 'viewBox',
    viewTarget: 'viewTarget',
    visibility: 0,
    widths: 0,
    wordSpacing: 'word-spacing',
    writingMode: 'writing-mode',
    x: 0,
    xHeight: 'x-height',
    x1: 0,
    x2: 0,
    xChannelSelector: 'xChannelSelector',
    xlinkActuate: 'xlink:actuate',
    xlinkArcrole: 'xlink:arcrole',
    xlinkHref: 'xlink:href',
    xlinkRole: 'xlink:role',
    xlinkShow: 'xlink:show',
    xlinkTitle: 'xlink:title',
    xlinkType: 'xlink:type',
    xmlBase: 'xml:base',
    xmlns: 0,
    xmlnsXlink: 'xmlns:xlink',
    xmlLang: 'xml:lang',
    xmlSpace: 'xml:space',
    y: 0,
    y1: 0,
    y2: 0,
    yChannelSelector: 'yChannelSelector',
    z: 0,
    zoomAndPan: 'zoomAndPan'
};

var SVGDOMPropertyConfig = {
    props: {},
    attrNS: {
        xlinkActuate: xlink,
        xlinkArcrole: xlink,
        xlinkHref: xlink,
        xlinkRole: xlink,
        xlinkShow: xlink,
        xlinkTitle: xlink,
        xlinkType: xlink,
        xmlBase: xml,
        xmlLang: xml,
        xmlSpace: xml
    },
    domAttrs: {},
    domProps: {}
};

Object.keys(ATTRS).map(function (key) {
    SVGDOMPropertyConfig.props[key] = 0;
    if (ATTRS[key]) {
        SVGDOMPropertyConfig.domAttrs[key] = ATTRS[key];
    }
});

// merge html and svg config into properties
mergeConfigToProperties(HTMLDOMPropertyConfig);
mergeConfigToProperties(SVGDOMPropertyConfig);

function mergeConfigToProperties(config) {
    var
    // all react/react-lite supporting property names in here
    props = config.props;
    var
    // attributes namespace in here
    attrNS = config.attrNS;
    var
    // propName in props which should use to be dom-attribute in here
    domAttrs = config.domAttrs;
    var
    // propName in props which should use to be dom-property in here
    domProps = config.domProps;

    for (var propName in props) {
        if (!props.hasOwnProperty(propName)) {
            continue;
        }
        var propConfig = props[propName];
        properties[propName] = {
            attributeName: domAttrs.hasOwnProperty(propName) ? domAttrs[propName] : propName.toLowerCase(),
            propertyName: domProps.hasOwnProperty(propName) ? domProps[propName] : propName,
            attributeNamespace: attrNS.hasOwnProperty(propName) ? attrNS[propName] : null,
            mustUseProperty: checkMask(propConfig, MUST_USE_PROPERTY),
            hasBooleanValue: checkMask(propConfig, HAS_BOOLEAN_VALUE),
            hasNumericValue: checkMask(propConfig, HAS_NUMERIC_VALUE),
            hasPositiveNumericValue: checkMask(propConfig, HAS_POSITIVE_NUMERIC_VALUE),
            hasOverloadedBooleanValue: checkMask(propConfig, HAS_OVERLOADED_BOOLEAN_VALUE)
        };
    }
}

function checkMask(value, bitmask) {
    return (value & bitmask) === bitmask;
}

/**
 * Sets the value for a property on a node.
 *
 * @param {DOMElement} node
 * @param {string} name
 * @param {*} value
 */

function setPropValue(node, name, value) {
    var propInfo = properties.hasOwnProperty(name) && properties[name];
    if (propInfo) {
        // should delete value from dom
        if (value == null || propInfo.hasBooleanValue && !value || propInfo.hasNumericValue && isNaN(value) || propInfo.hasPositiveNumericValue && value < 1 || propInfo.hasOverloadedBooleanValue && value === false) {
            removePropValue(node, name);
        } else if (propInfo.mustUseProperty) {
            var propName = propInfo.propertyName;
            // dom.value has side effect
            if (propName !== 'value' || '' + node[propName] !== '' + value) {
                node[propName] = value;
            }
        } else {
            var attributeName = propInfo.attributeName;
            var namespace = propInfo.attributeNamespace;

            // `setAttribute` with objects becomes only `[object]` in IE8/9,
            // ('' + value) makes it output the correct toString()-value.
            if (namespace) {
                node.setAttributeNS(namespace, attributeName, '' + value);
            } else if (propInfo.hasBooleanValue || propInfo.hasOverloadedBooleanValue && value === true) {
                node.setAttribute(attributeName, '');
            } else {
                node.setAttribute(attributeName, '' + value);
            }
        }
    } else if (isCustomAttribute(name) && VALID_ATTRIBUTE_NAME_REGEX.test(name)) {
        if (value == null) {
            node.removeAttribute(name);
        } else {
            node.setAttribute(name, '' + value);
        }
    }
}

/**
 * Deletes the value for a property on a node.
 *
 * @param {DOMElement} node
 * @param {string} name
 */

function removePropValue(node, name) {
    var propInfo = properties.hasOwnProperty(name) && properties[name];
    if (propInfo) {
        if (propInfo.mustUseProperty) {
            var propName = propInfo.propertyName;
            if (propInfo.hasBooleanValue) {
                node[propName] = false;
            } else {
                // dom.value accept string value has side effect
                if (propName !== 'value' || '' + node[propName] !== '') {
                    node[propName] = '';
                }
            }
        } else {
            node.removeAttribute(propInfo.attributeName);
        }
    } else if (isCustomAttribute(name)) {
        node.removeAttribute(name);
    }
}

function isFn(obj) {
    return typeof obj === 'function';
}

var isArr = Array.isArray;

function noop() {}

function identity(obj) {
    return obj;
}

function pipe(fn1, fn2) {
    return function () {
        fn1.apply(this, arguments);
        return fn2.apply(this, arguments);
    };
}

function addItem(list, item) {
    list[list.length] = item;
}

function flatEach(list, iteratee, a) {
    var len = list.length;
    var i = -1;

    while (len--) {
        var item = list[++i];
        if (isArr(item)) {
            flatEach(item, iteratee, a);
        } else {
            iteratee(item, a);
        }
    }
}

function extend(to, from) {
    if (!from) {
        return to;
    }
    var keys = Object.keys(from);
    var i = keys.length;
    while (i--) {
        to[keys[i]] = from[keys[i]];
    }
    return to;
}

var uid = 0;

function getUid() {
    return ++uid;
}

var EVENT_KEYS = /^on/i;

function setProp(elem, key, value, isCustomComponent) {
    if (EVENT_KEYS.test(key)) {
        addEvent(elem, key, value);
    } else if (key === 'style') {
        setStyle(elem.style, value);
    } else if (key === HTML_KEY) {
        if (value && value.__html != null) {
            elem.innerHTML = value.__html;
        }
    } else if (isCustomComponent) {
        if (value == null) {
            elem.removeAttribute(key);
        } else {
            elem.setAttribute(key, '' + value);
        }
    } else {
        setPropValue(elem, key, value);
    }
}

function removeProp(elem, key, oldValue, isCustomComponent) {
    if (EVENT_KEYS.test(key)) {
        removeEvent(elem, key);
    } else if (key === 'style') {
        removeStyle(elem.style, oldValue);
    } else if (key === HTML_KEY) {
        elem.innerHTML = '';
    } else if (isCustomComponent) {
        elem.removeAttribute(key);
    } else {
        removePropValue(elem, key);
    }
}

function patchProp(elem, key, value, oldValue, isCustomComponent) {
    if (key === 'value' || key === 'checked') {
        oldValue = elem[key];
    }
    if (value === oldValue) {
        return;
    }
    if (value === undefined) {
        removeProp(elem, key, oldValue, isCustomComponent);
        return;
    }
    if (key === 'style') {
        patchStyle(elem.style, oldValue, value);
    } else {
        setProp(elem, key, value, isCustomComponent);
    }
}

function setProps(elem, props, isCustomComponent) {
    for (var key in props) {
        if (key !== 'children') {
            setProp(elem, key, props[key], isCustomComponent);
        }
    }
}

function patchProps(elem, props, newProps, isCustomComponent) {
    for (var key in props) {
        if (key !== 'children') {
            if (newProps.hasOwnProperty(key)) {
                patchProp(elem, key, newProps[key], props[key], isCustomComponent);
            } else {
                removeProp(elem, key, props[key], isCustomComponent);
            }
        }
    }
    for (var key in newProps) {
        if (key !== 'children' && !props.hasOwnProperty(key)) {
            setProp(elem, key, newProps[key], isCustomComponent);
        }
    }
}

if (!Object.freeze) {
    Object.freeze = identity;
}

function isValidContainer(node) {
	return !!(node && (node.nodeType === ELEMENT_NODE_TYPE || node.nodeType === DOC_NODE_TYPE || node.nodeType === DOCUMENT_FRAGMENT_NODE_TYPE));
}

var pendingRendering = {};
var vnodeStore = {};
function renderTreeIntoContainer(vnode, container, callback, parentContext) {
	if (!vnode.vtype) {
		throw new Error('cannot render ' + vnode + ' to container');
	}
	if (!isValidContainer(container)) {
		throw new Error('container ' + container + ' is not a DOM element');
	}
	var id = container[COMPONENT_ID] || (container[COMPONENT_ID] = getUid());
	var argsCache = pendingRendering[id];

	// component lify cycle method maybe call root rendering
	// should bundle them and render by only one time
	if (argsCache) {
		if (argsCache === true) {
			pendingRendering[id] = argsCache = { vnode: vnode, callback: callback, parentContext: parentContext };
		} else {
			argsCache.vnode = vnode;
			argsCache.parentContext = parentContext;
			argsCache.callback = argsCache.callback ? pipe(argsCache.callback, callback) : callback;
		}
		return;
	}

	pendingRendering[id] = true;
	var oldVnode = null;
	var rootNode = null;
	if (oldVnode = vnodeStore[id]) {
		rootNode = compareTwoVnodes(oldVnode, vnode, container.firstChild, parentContext);
	} else {
		rootNode = initVnode(vnode, parentContext, container.namespaceURI);
		var childNode = null;
		while (childNode = container.lastChild) {
			container.removeChild(childNode);
		}
		container.appendChild(rootNode);
	}
	vnodeStore[id] = vnode;
	var isPending = updateQueue.isPending;
	updateQueue.isPending = true;
	clearPending();
	argsCache = pendingRendering[id];
	delete pendingRendering[id];

	var result = null;
	if (typeof argsCache === 'object') {
		result = renderTreeIntoContainer(argsCache.vnode, container, argsCache.callback, argsCache.parentContext);
	} else if (vnode.vtype === VELEMENT) {
		result = rootNode;
	} else if (vnode.vtype === VCOMPONENT) {
		result = rootNode.cache[vnode.uid];
	}

	if (!isPending) {
		updateQueue.isPending = false;
		updateQueue.batchUpdate();
	}

	if (callback) {
		callback.call(result);
	}

	return result;
}

function render(vnode, container, callback) {
	return renderTreeIntoContainer(vnode, container, callback);
}

function unstable_renderSubtreeIntoContainer(parentComponent, subVnode, container, callback) {
	var context = parentComponent.$cache.parentContext;
	return renderTreeIntoContainer(subVnode, container, callback, context);
}

function unmountComponentAtNode(container) {
	if (!container.nodeName) {
		throw new Error('expect node');
	}
	var id = container[COMPONENT_ID];
	var vnode = null;
	if (vnode = vnodeStore[id]) {
		destroyVnode(vnode, container.firstChild);
		container.removeChild(container.firstChild);
		delete vnodeStore[id];
		return true;
	}
	return false;
}

function findDOMNode(node) {
	if (node == null) {
		return null;
	}
	if (node.nodeName) {
		return node;
	}
	var component = node;
	// if component.node equal to false, component must be unmounted
	if (component.getDOMNode && component.$cache.isMounted) {
		return component.getDOMNode();
	}
	throw new Error('findDOMNode can not find Node');
}

var ReactDOM = Object.freeze({
	render: render,
	unstable_renderSubtreeIntoContainer: unstable_renderSubtreeIntoContainer,
	unmountComponentAtNode: unmountComponentAtNode,
	findDOMNode: findDOMNode
});

function createElement(type, props, children) {
	var vtype = null;
	if (typeof type === 'string') {
		vtype = VELEMENT;
	} else if (typeof type === 'function') {
		if (type.prototype && type.prototype.isReactComponent) {
			vtype = VCOMPONENT;
		} else {
			vtype = VSTATELESS;
		}
	} else {
		throw new Error('React.createElement: unexpect type [ ' + type + ' ]');
	}

	var key = null;
	var ref = null;
	var finalProps = {};
	if (props != null) {
		for (var propKey in props) {
			if (!props.hasOwnProperty(propKey)) {
				continue;
			}
			if (propKey === 'key') {
				if (props.key !== undefined) {
					key = '' + props.key;
				}
			} else if (propKey === 'ref') {
				if (props.ref !== undefined) {
					ref = props.ref;
				}
			} else {
				finalProps[propKey] = props[propKey];
			}
		}
	}

	var defaultProps = type.defaultProps;

	if (defaultProps) {
		for (var propKey in defaultProps) {
			if (finalProps[propKey] === undefined) {
				finalProps[propKey] = defaultProps[propKey];
			}
		}
	}

	var argsLen = arguments.length;
	var finalChildren = children;

	if (argsLen > 3) {
		finalChildren = Array(argsLen - 2);
		for (var i = 2; i < argsLen; i++) {
			finalChildren[i - 2] = arguments[i];
		}
	}

	if (finalChildren !== undefined) {
		finalProps.children = finalChildren;
	}

	return createVnode(vtype, type, finalProps, key, ref);
}

function isValidElement(obj) {
	return obj != null && !!obj.vtype;
}

function cloneElement(originElem, props) {
	var type = originElem.type;
	var key = originElem.key;
	var ref = originElem.ref;

	var newProps = extend(extend({ key: key, ref: ref }, originElem.props), props);

	for (var _len = arguments.length, children = Array(_len > 2 ? _len - 2 : 0), _key = 2; _key < _len; _key++) {
		children[_key - 2] = arguments[_key];
	}

	var vnode = createElement.apply(undefined, [type, newProps].concat(children));
	if (vnode.ref === originElem.ref) {
		vnode.refs = originElem.refs;
	}
	return vnode;
}

function createFactory(type) {
	var factory = function factory() {
		for (var _len2 = arguments.length, args = Array(_len2), _key2 = 0; _key2 < _len2; _key2++) {
			args[_key2] = arguments[_key2];
		}

		return createElement.apply(undefined, [type].concat(args));
	};
	factory.type = type;
	return factory;
}

var tagNames = 'a|abbr|address|area|article|aside|audio|b|base|bdi|bdo|big|blockquote|body|br|button|canvas|caption|cite|code|col|colgroup|data|datalist|dd|del|details|dfn|dialog|div|dl|dt|em|embed|fieldset|figcaption|figure|footer|form|h1|h2|h3|h4|h5|h6|head|header|hgroup|hr|html|i|iframe|img|input|ins|kbd|keygen|label|legend|li|link|main|map|mark|menu|menuitem|meta|meter|nav|noscript|object|ol|optgroup|option|output|p|param|picture|pre|progress|q|rp|rt|ruby|s|samp|script|section|select|small|source|span|strong|style|sub|summary|sup|table|tbody|td|textarea|tfoot|th|thead|time|title|tr|track|u|ul|var|video|wbr|circle|clipPath|defs|ellipse|g|image|line|linearGradient|mask|path|pattern|polygon|polyline|radialGradient|rect|stop|svg|text|tspan';
var DOM = {};
tagNames.split('|').forEach(function (tagName) {
	DOM[tagName] = createFactory(tagName);
});

var check = function check() {
    return check;
};
check.isRequired = check;
var PropTypes = {
    "array": check,
    "bool": check,
    "func": check,
    "number": check,
    "object": check,
    "string": check,
    "any": check,
    "arrayOf": check,
    "element": check,
    "instanceOf": check,
    "node": check,
    "objectOf": check,
    "oneOf": check,
    "oneOfType": check,
    "shape": check
};

function only(children) {
	if (isValidElement(children)) {
		return children;
	}
	throw new Error('expect only one child');
}

function forEach(children, iteratee, context) {
	if (children == null) {
		return children;
	}
	var index = 0;
	if (isArr(children)) {
		flatEach(children, function (child) {
			iteratee.call(context, child, index++);
		});
	} else {
		iteratee.call(context, children, index);
	}
}

function map(children, iteratee, context) {
	if (children == null) {
		return children;
	}
	var store = [];
	var keyMap = {};
	forEach(children, function (child, index) {
		var data = {};
		data.child = iteratee.call(context, child, index) || child;
		data.isEqual = data.child === child;
		var key = data.key = getKey(child, index);
		if (keyMap.hasOwnProperty(key)) {
			keyMap[key] += 1;
		} else {
			keyMap[key] = 0;
		}
		data.index = keyMap[key];
		addItem(store, data);
	});
	var result = [];
	store.forEach(function (_ref) {
		var child = _ref.child;
		var key = _ref.key;
		var index = _ref.index;
		var isEqual = _ref.isEqual;

		if (child == null || typeof child === 'boolean') {
			return;
		}
		if (!isValidElement(child) || key == null) {
			addItem(result, child);
			return;
		}
		if (keyMap[key] !== 0) {
			key += ':' + index;
		}
		if (!isEqual) {
			key = escapeUserProvidedKey(child.key || '') + '/' + key;
		}
		child = cloneElement(child, { key: key });
		addItem(result, child);
	});
	return result;
}

function count(children) {
	var count = 0;
	forEach(children, function () {
		count++;
	});
	return count;
}

function toArray(children) {
	return map(children, identity) || [];
}

function getKey(child, index) {
	var key = undefined;
	if (isValidElement(child) && typeof child.key === 'string') {
		key = '.$' + child.key;
	} else {
		key = '.' + index.toString(36);
	}
	return key;
}

var userProvidedKeyEscapeRegex = /\/(?!\/)/g;
function escapeUserProvidedKey(text) {
	return ('' + text).replace(userProvidedKeyEscapeRegex, '//');
}

var Children = Object.freeze({
	only: only,
	forEach: forEach,
	map: map,
	count: count,
	toArray: toArray
});

function eachMixin(mixins, iteratee) {
	mixins.forEach(function (mixin) {
		if (mixin) {
			if (isArr(mixin.mixins)) {
				eachMixin(mixin.mixins, iteratee);
			}
			iteratee(mixin);
		}
	});
}

function combineMixinToProto(proto, mixin) {
	for (var key in mixin) {
		if (!mixin.hasOwnProperty(key)) {
			continue;
		}
		var value = mixin[key];
		if (key === 'getInitialState') {
			addItem(proto.$getInitialStates, value);
			continue;
		}
		var curValue = proto[key];
		if (isFn(curValue) && isFn(value)) {
			proto[key] = pipe(curValue, value);
		} else {
			proto[key] = value;
		}
	}
}

function combineMixinToClass(Component, mixin) {
	if (mixin.propTypes) {
		Component.propTypes = Component.propTypes || {};
		extend(Component.propTypes, mixin.propTypes);
	}
	if (mixin.contextTypes) {
		Component.contextTypes = Component.contextTypes || {};
		extend(Component.contextTypes, mixin.contextTypes);
	}
	extend(Component, mixin.statics);
	if (isFn(mixin.getDefaultProps)) {
		Component.defaultProps = Component.defaultProps || {};
		extend(Component.defaultProps, mixin.getDefaultProps());
	}
}

function bindContext(obj, source) {
	for (var key in source) {
		if (source.hasOwnProperty(key)) {
			if (isFn(source[key])) {
				obj[key] = source[key].bind(obj);
			}
		}
	}
}

var Facade = function Facade() {};
Facade.prototype = Component.prototype;

function getInitialState() {
	var _this = this;

	var state = {};
	var setState = this.setState;
	this.setState = Facade;
	this.$getInitialStates.forEach(function (getInitialState) {
		if (isFn(getInitialState)) {
			extend(state, getInitialState.call(_this));
		}
	});
	this.setState = setState;
	return state;
}
function createClass(spec) {
	if (!isFn(spec.render)) {
		throw new Error('createClass: spec.render is not function');
	}
	var specMixins = spec.mixins || [];
	var mixins = specMixins.concat(spec);
	spec.mixins = null;
	function Klass(props, context) {
		Component.call(this, props, context);
		this.constructor = Klass;
		spec.autobind !== false && bindContext(this, Klass.prototype);
		this.state = this.getInitialState() || this.state;
	}
	Klass.displayName = spec.displayName;
	var proto = Klass.prototype = new Facade();
	proto.$getInitialStates = [];
	eachMixin(mixins, function (mixin) {
		combineMixinToProto(proto, mixin);
		combineMixinToClass(Klass, mixin);
	});
	proto.getInitialState = getInitialState;
	spec.mixins = specMixins;
	return Klass;
}

function shallowEqual(objA, objB) {
    if (objA === objB) {
        return true;
    }

    if (typeof objA !== 'object' || objA === null || typeof objB !== 'object' || objB === null) {
        return false;
    }

    var keysA = Object.keys(objA);
    var keysB = Object.keys(objB);

    if (keysA.length !== keysB.length) {
        return false;
    }

    // Test for A's keys different from B.
    for (var i = 0; i < keysA.length; i++) {
        if (!objB.hasOwnProperty(keysA[i]) || objA[keysA[i]] !== objB[keysA[i]]) {
            return false;
        }
    }

    return true;
}

function PureComponent(props, context) {
	Component.call(this, props, context);
}

PureComponent.prototype = Object.create(Component.prototype);
PureComponent.prototype.constructor = PureComponent;
PureComponent.prototype.isPureReactComponent = true;
PureComponent.prototype.shouldComponentUpdate = shallowCompare;

function shallowCompare(nextProps, nextState) {
	return !shallowEqual(this.props, nextProps) || !shallowEqual(this.state, nextState);
}

var React = extend({
    version: '0.15.1',
    cloneElement: cloneElement,
    isValidElement: isValidElement,
    createElement: createElement,
    createFactory: createFactory,
    Component: Component,
    PureComponent: PureComponent,
    createClass: createClass,
    Children: Children,
    PropTypes: PropTypes,
    DOM: DOM
}, ReactDOM);

React.__SECRET_DOM_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = ReactDOM;

module.exports = React;

/***/ }),
/* 1 */
/* no static exports found */
/* all exports used */
/*!************************!*\
  !*** ./src/helpers.js ***!
  \************************/
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.getTableErrorGroups = getTableErrorGroups;
exports.removeBaseUrl = removeBaseUrl;
exports.merge = merge;
// Module API

function getTableErrorGroups(table) {
  var groups = {};
  var _iteratorNormalCompletion = true;
  var _didIteratorError = false;
  var _iteratorError = undefined;

  try {
    for (var _iterator = table.errors[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
      var error = _step.value;


      // Get group
      var group = groups[error.code];

      // Create group
      if (!group) {
        group = {
          code: error.code,
          rows: {},
          count: 0,
          headers: table.headers,
          messages: []
        };
      }

      // Get row
      var row = group.rows[error['row-number']];

      // Create row
      if (!row) {
        var values = error.row;
        if (!error['row-number']) {
          values = table.headers;
        }
        row = {
          values: values,
          badcols: new Set()
        };
      }

      // Ensure missing value
      if (error.code === 'missing-value') {
        row.values[error['column-number'] - 1] = '';
      }

      // Add row badcols
      if (error['column-number']) {
        row.badcols.add(error['column-number']);
      } else if (row.values) {
        row.badcols = new Set(row.values.map(function (value, index) {
          return index + 1;
        }));
      }

      // Save group
      group.count += 1;
      group.messages.push(error.message);
      group.rows[error['row-number']] = row;
      groups[error.code] = group;
    }
  } catch (err) {
    _didIteratorError = true;
    _iteratorError = err;
  } finally {
    try {
      if (!_iteratorNormalCompletion && _iterator.return) {
        _iterator.return();
      }
    } finally {
      if (_didIteratorError) {
        throw _iteratorError;
      }
    }
  }

  return groups;
}

function removeBaseUrl(text) {
  return text.replace(/https:\/\/raw\.githubusercontent\.com\/\S*?\/\S*?\/\S*?\//g, '');
}

function merge() {
  for (var _len = arguments.length, args = Array(_len), _key = 0; _key < _len; _key++) {
    args[_key] = arguments[_key];
  }

  return Object.assign.apply(Object, [{}].concat(args));
}

/***/ }),
/* 2 */
/* no static exports found */
/* all exports used */
/*!*****************************!*\
  !*** ./~/lodash/_Symbol.js ***!
  \*****************************/
/***/ (function(module, exports, __webpack_require__) {

var root = __webpack_require__(/*! ./_root */ 31);

/** Built-in value references. */
var Symbol = root.Symbol;

module.exports = Symbol;


/***/ }),
/* 3 */
/* no static exports found */
/* all exports used */
/*!******************************!*\
  !*** ./~/lodash/toString.js ***!
  \******************************/
/***/ (function(module, exports, __webpack_require__) {

var baseToString = __webpack_require__(/*! ./_baseToString */ 22);

/**
 * Converts `value` to a string. An empty string is returned for `null`
 * and `undefined` values. The sign of `-0` is preserved.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to convert.
 * @returns {string} Returns the converted string.
 * @example
 *
 * _.toString(null);
 * // => ''
 *
 * _.toString(-0);
 * // => '-0'
 *
 * _.toString([1, 2, 3]);
 * // => '1,2,3'
 */
function toString(value) {
  return value == null ? '' : baseToString(value);
}

module.exports = toString;


/***/ }),
/* 4 */
/* no static exports found */
/* all exports used */
/*!**********************************!*\
  !*** ./src/components/Report.js ***!
  \**********************************/
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.Report = Report;

var _react = __webpack_require__(/*! react */ 0);

var _react2 = _interopRequireDefault(_react);

var _helpers = __webpack_require__(/*! ../helpers */ 1);

var _InvalidTable = __webpack_require__(/*! ./InvalidTable */ 12);

var _MessageGroup = __webpack_require__(/*! ./MessageGroup */ 5);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

// Module API

function Report(_ref) {
  var report = _ref.report;

  var processedWarnings = getProcessedWarnings(report);
  var validTableFiles = getValidTableFiles(report);
  var invalidTables = getInvalidTables(report);
  return _react2.default.createElement(
    'div',
    { className: 'goodtables-ui-report' },
    !!processedWarnings.length && _react2.default.createElement(_MessageGroup.MessageGroup, {
      type: 'warning',
      title: 'There are ' + processedWarnings.length + ' warning(s)',
      expandText: 'Warning details',
      messages: processedWarnings
    }),
    !!validTableFiles.length && _react2.default.createElement(_MessageGroup.MessageGroup, {
      type: 'success',
      title: 'There are ' + validTableFiles.length + ' valid table(s)',
      expandText: 'Success details',
      messages: validTableFiles
    }),
    invalidTables.map(function (table, index) {
      return _react2.default.createElement(_InvalidTable.InvalidTable, {
        key: table.source,
        table: table,
        tableNumber: index + 1,
        tablesCount: invalidTables.length
      });
    })
  );
}

// Internal

function getProcessedWarnings(report) {
  // Before `goodtables@1.0` there was no warnings property
  return (report.warnings || []).map(function (warning) {
    return (0, _helpers.removeBaseUrl)(warning);
  });
}

function getValidTableFiles(report) {
  return report.tables.filter(function (table) {
    return table.valid;
  }).map(function (table) {
    return (0, _helpers.removeBaseUrl)(table.source);
  });
}

function getInvalidTables(report) {
  return report.tables.filter(function (table) {
    return !table.valid;
  });
}

/***/ }),
/* 5 */
/* no static exports found */
/* all exports used */
/*!****************************************!*\
  !*** ./src/components/MessageGroup.js ***!
  \****************************************/
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.MessageGroup = undefined;

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(/*! react */ 0);

var _react2 = _interopRequireDefault(_react);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

// Module API

var MessageGroup = exports.MessageGroup = function (_React$Component) {
  _inherits(MessageGroup, _React$Component);

  // Public

  function MessageGroup(_ref) {
    var type = _ref.type,
        title = _ref.title,
        messages = _ref.messages,
        expandText = _ref.expandText;

    _classCallCheck(this, MessageGroup);

    var _this = _possibleConstructorReturn(this, (MessageGroup.__proto__ || Object.getPrototypeOf(MessageGroup)).call(this, { type: type, title: title, messages: messages, expandText: expandText }));

    _this.state = {
      isExpanded: false
    };
    return _this;
  }

  _createClass(MessageGroup, [{
    key: "render",
    value: function render() {
      var _this2 = this;

      var _props = this.props,
          type = _props.type,
          title = _props.title,
          messages = _props.messages,
          expandText = _props.expandText;
      var isExpanded = this.state.isExpanded;

      return _react2.default.createElement(
        "div",
        { className: "alert alert-" + type, role: "alert" },
        _react2.default.createElement(
          "span",
          { className: "title", onClick: function onClick() {
              return _this2.setState({ isExpanded: !isExpanded });
            } },
          title
        ),
        _react2.default.createElement(
          "a",
          { className: "show-details", onClick: function onClick() {
              return _this2.setState({ isExpanded: !isExpanded });
            } },
          expandText
        ),
        isExpanded && _react2.default.createElement(
          "div",
          null,
          _react2.default.createElement("hr", null),
          _react2.default.createElement(
            "ul",
            null,
            messages.map(function (message) {
              return _react2.default.createElement(
                "li",
                null,
                message
              );
            })
          )
        )
      );
    }
  }]);

  return MessageGroup;
}(_react2.default.Component);

/***/ }),
/* 6 */
/* no static exports found */
/* all exports used */
/*!*********************************!*\
  !*** ./~/lodash/_hasUnicode.js ***!
  \*********************************/
/***/ (function(module, exports) {

/** Used to compose unicode character classes. */
var rsAstralRange = '\\ud800-\\udfff',
    rsComboMarksRange = '\\u0300-\\u036f',
    reComboHalfMarksRange = '\\ufe20-\\ufe2f',
    rsComboSymbolsRange = '\\u20d0-\\u20ff',
    rsComboRange = rsComboMarksRange + reComboHalfMarksRange + rsComboSymbolsRange,
    rsVarRange = '\\ufe0e\\ufe0f';

/** Used to compose unicode capture groups. */
var rsZWJ = '\\u200d';

/** Used to detect strings with [zero-width joiners or code points from the astral planes](http://eev.ee/blog/2015/09/12/dark-corners-of-unicode/). */
var reHasUnicode = RegExp('[' + rsZWJ + rsAstralRange  + rsComboRange + rsVarRange + ']');

/**
 * Checks if `string` contains Unicode symbols.
 *
 * @private
 * @param {string} string The string to inspect.
 * @returns {boolean} Returns `true` if a symbol is found, else `false`.
 */
function hasUnicode(string) {
  return reHasUnicode.test(string);
}

module.exports = hasUnicode;


/***/ }),
/* 7 */
/* no static exports found */
/* all exports used */
/*!***********************************!*\
  !*** (webpack)/buildin/global.js ***!
  \***********************************/
/***/ (function(module, exports) {

var g;

// This works in non-strict mode
g = (function() {
	return this;
})();

try {
	// This works if eval is allowed (see CSP)
	g = g || Function("return this")() || (1,eval)("this");
} catch(e) {
	// This works if the window reference is available
	if(typeof window === "object")
		g = window;
}

// g can still be undefined, but nothing to do about it...
// We return undefined, instead of nothing here, so it's
// easier to handle this case. if(!global) { ...}

module.exports = g;


/***/ }),
/* 8 */
/* no static exports found */
/* all exports used */
/*!********************************!*\
  !*** ./src/components/Form.js ***!
  \********************************/
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.Form = undefined;

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(/*! react */ 0);

var _react2 = _interopRequireDefault(_react);

var _Report = __webpack_require__(/*! ./Report */ 4);

var _MessageGroup = __webpack_require__(/*! ./MessageGroup */ 5);

var _helpers = __webpack_require__(/*! ../helpers */ 1);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

// Module API

var Form = exports.Form = function (_React$Component) {
  _inherits(Form, _React$Component);

  // Public

  function Form(_ref) {
    var source = _ref.source,
        options = _ref.options,
        validate = _ref.validate,
        reportPromise = _ref.reportPromise;

    _classCallCheck(this, Form);

    // Set state
    var _this = _possibleConstructorReturn(this, (Form.__proto__ || Object.getPrototypeOf(Form)).call(this, { source: source, options: options, validate: validate, reportPromise: reportPromise }));

    _this.state = {
      isSourceFile: false,
      isSchemaFile: false,
      isLoading: !!reportPromise,
      source: source || '',
      options: options || {},
      report: null,
      error: null
    };

    // Load report
    if (_this.props.reportPromise) {
      _this.props.reportPromise.then(function (report) {
        _this.setState({ report: report, isLoading: false });
      }).catch(function (error) {
        _this.setState({ error: error, isLoading: false });
      });
    }
    return _this;
  }

  _createClass(Form, [{
    key: 'render',
    value: function render() {
      var _state = this.state,
          isSourceFile = _state.isSourceFile,
          isSchemaFile = _state.isSchemaFile,
          isLoading = _state.isLoading;
      var _state2 = this.state,
          source = _state2.source,
          options = _state2.options,
          report = _state2.report,
          error = _state2.error;

      var onSourceTypeChange = this.onSourceTypeChange.bind(this);
      var onSchemaTypeChange = this.onSchemaTypeChange.bind(this);
      var onSourceChange = this.onSourceChange.bind(this);
      var onOptionsChange = this.onOptionsChange.bind(this);
      var onSubmit = this.onSubmit.bind(this);
      return _react2.default.createElement(
        'form',
        { className: 'goodtables-ui-form panel panel-default' },
        _react2.default.createElement(
          'div',
          { className: 'row-source' },
          _react2.default.createElement(
            'div',
            { className: 'form-inline' },
            _react2.default.createElement(
              'label',
              { htmlFor: 'source' },
              'Source'
            ),
            '\xA0 [',
            _react2.default.createElement(
              'a',
              { href: '#', onClick: function onClick() {
                  return onSourceTypeChange();
                } },
              isSourceFile ? 'Provide Link' : 'Upload File'
            ),
            ']',
            _react2.default.createElement(
              'div',
              { className: 'input-group', style: { width: '100%' } },
              !isSourceFile && _react2.default.createElement('input', {
                name: 'source',
                className: 'form-control',
                type: 'text',
                value: source,
                placeholder: 'http://data.source/url',
                onChange: function onChange(ev) {
                  return onSourceChange(ev.target.value);
                }
              }),
              isSourceFile && _react2.default.createElement('input', {
                name: 'source',
                className: 'form-control',
                type: 'file',
                placeholder: 'http://data.source/url',
                onChange: function onChange(ev) {
                  return onSourceChange(ev.target.files[0]);
                }
              }),
              _react2.default.createElement(
                'div',
                { className: 'input-group-btn', style: { width: '1%' } },
                _react2.default.createElement(
                  'button',
                  {
                    className: 'btn btn-success',
                    onClick: function onClick(ev) {
                      ev.preventDefault();onSubmit();
                    }
                  },
                  'Validate'
                )
              )
            ),
            _react2.default.createElement(
              'small',
              null,
              _react2.default.createElement(
                'strong',
                null,
                '[REQUIRED]'
              ),
              ' Add a data table to validate.'
            )
          )
        ),
        _react2.default.createElement(
          'div',
          { className: 'row-schema' },
          _react2.default.createElement(
            'div',
            { className: 'row' },
            _react2.default.createElement(
              'div',
              { className: 'form-group col-md-8' },
              _react2.default.createElement(
                'label',
                { htmlFor: 'schema' },
                'Schema'
              ),
              '\xA0 [',
              _react2.default.createElement(
                'a',
                { href: '#', onClick: function onClick() {
                    return onSchemaTypeChange();
                  } },
                isSchemaFile ? 'Provide Link' : 'Upload File'
              ),
              ']',
              !isSchemaFile && _react2.default.createElement('input', {
                type: 'text',
                className: 'form-control',
                name: 'schema',
                value: options.schema,
                placeholder: 'http://table.schema/url',
                onChange: function onChange(ev) {
                  return onOptionsChange('schema', ev.target.value);
                }
              }),
              isSchemaFile && _react2.default.createElement('input', {
                type: 'file',
                className: 'form-control',
                name: 'schema',
                placeholder: 'http://table.schema/url',
                onChange: function onChange(ev) {
                  return onOptionsChange('schema', ev.target.files[0]);
                }
              }),
              _react2.default.createElement(
                'small',
                null,
                _react2.default.createElement(
                  'strong',
                  null,
                  '[OPTIONAL]'
                ),
                ' Select to validate this data against a Table Schema (',
                _react2.default.createElement(
                  'a',
                  { href: 'http://specs.frictionlessdata.io/table-schema/', target: '_blank', rel: 'noopener noreferrer' },
                  'What is it?'
                ),
                ').'
              )
            ),
            _react2.default.createElement(
              'div',
              { className: 'form-group col-md-2' },
              _react2.default.createElement(
                'div',
                { className: 'form-group' },
                _react2.default.createElement(
                  'label',
                  { htmlFor: 'format' },
                  'Format'
                ),
                _react2.default.createElement(
                  'select',
                  {
                    name: 'format',
                    value: options.format,
                    className: 'form-control',
                    onChange: function onChange(ev) {
                      return onOptionsChange('format', ev.target.value);
                    }
                  },
                  _react2.default.createElement(
                    'option',
                    { value: '' },
                    'Auto'
                  ),
                  _react2.default.createElement(
                    'option',
                    { value: 'csv' },
                    'CSV'
                  ),
                  _react2.default.createElement(
                    'option',
                    { value: 'gsheet' },
                    'Google Sheet'
                  ),
                  _react2.default.createElement(
                    'option',
                    { value: 'json' },
                    'JSON'
                  ),
                  _react2.default.createElement(
                    'option',
                    { value: 'ndjson' },
                    'NDJSON'
                  ),
                  _react2.default.createElement(
                    'option',
                    { value: 'ods' },
                    'ODS'
                  ),
                  _react2.default.createElement(
                    'option',
                    { value: 'tsv' },
                    'TSV'
                  ),
                  _react2.default.createElement(
                    'option',
                    { value: 'xls' },
                    'XLS'
                  ),
                  _react2.default.createElement(
                    'option',
                    { value: 'xlsx' },
                    'XLSX'
                  )
                )
              )
            ),
            _react2.default.createElement(
              'div',
              { className: 'col-md-2' },
              _react2.default.createElement(
                'div',
                { className: 'form-group' },
                _react2.default.createElement(
                  'label',
                  { htmlFor: 'encoding' },
                  'Encoding'
                ),
                _react2.default.createElement(
                  'select',
                  {
                    name: 'encoding',
                    value: options.encoding,
                    className: 'form-control',
                    onChange: function onChange(ev) {
                      return onOptionsChange('encoding', ev.target.value);
                    }
                  },
                  _react2.default.createElement(
                    'option',
                    { value: '' },
                    'Auto'
                  ),
                  _react2.default.createElement(
                    'option',
                    { value: 'utf-8' },
                    'UTF-8'
                  ),
                  _react2.default.createElement(
                    'option',
                    { value: 'ascii' },
                    'ASCII'
                  ),
                  _react2.default.createElement(
                    'option',
                    { value: 'iso-8859-2' },
                    'ISO-8859-2'
                  )
                )
              )
            )
          )
        ),
        _react2.default.createElement(
          'div',
          { className: 'row-flags' },
          _react2.default.createElement(
            'div',
            { className: 'row' },
            _react2.default.createElement(
              'div',
              { className: 'col-md-4' },
              _react2.default.createElement(
                'div',
                { className: 'checkbox' },
                _react2.default.createElement(
                  'label',
                  { htmlFor: 'errorLimit' },
                  _react2.default.createElement('input', {
                    name: 'errorLimit',
                    type: 'checkbox',
                    checked: options.errorLimit === 1,
                    onChange: function onChange(ev) {
                      onOptionsChange('errorLimit', ev.target.checked ? 1 : null);
                    }
                  }),
                  'Stop on first error'
                )
              ),
              _react2.default.createElement(
                'small',
                null,
                'Indicate whether validation should stop on the first error, or attempt to collect all errors.'
              )
            ),
            _react2.default.createElement(
              'div',
              { className: 'col-md-4' },
              _react2.default.createElement(
                'div',
                { className: 'checkbox' },
                _react2.default.createElement(
                  'label',
                  { htmlFor: 'ignoreBlankRows' },
                  _react2.default.createElement('input', {
                    name: 'ignoreBlankRows',
                    type: 'checkbox',
                    checked: (options.checks || {})['blank-row'] === false,
                    onChange: function onChange(ev) {
                      if (ev.target.checked) {
                        if (!(options.checks instanceof Object)) options.checks = {};
                        options.checks['blank-row'] = false;
                      } else {
                        if (options.checks instanceof Object) {
                          delete options.checks['blank-row'];
                        }
                      }
                    }
                  }),
                  'Ignore blank rows'
                )
              ),
              _react2.default.createElement(
                'small',
                null,
                'Indicate whether blank rows should be considered as errors, or simply ignored.'
              )
            ),
            _react2.default.createElement(
              'div',
              { className: 'col-md-4' },
              _react2.default.createElement(
                'div',
                { className: 'checkbox' },
                _react2.default.createElement(
                  'label',
                  { htmlFor: 'ignoreDuplicateRows' },
                  _react2.default.createElement('input', {
                    name: 'ignoreDuplicateRows',
                    type: 'checkbox',
                    checked: (options.checks || {})['duplicate-row'] === false,
                    onChange: function onChange(ev) {
                      if (ev.target.checked) {
                        if (!(options.checks instanceof Object)) options.checks = {};
                        options.checks['duplicate-row'] = false;
                      } else {
                        if (options.checks instanceof Object) {
                          delete options.checks['duplicate-row'];
                        }
                      }
                    }
                  }),
                  'Ignore duplicate rows'
                )
              ),
              _react2.default.createElement(
                'small',
                null,
                'Indicate whether duplicate rows should be considered as errors, or simply ignored.'
              )
            )
          )
        ),
        isLoading && _react2.default.createElement(
          'div',
          { className: 'row-message' },
          _react2.default.createElement(
            'div',
            { className: 'alert alert-info' },
            'Loading...'
          )
        ),
        error && _react2.default.createElement(
          'div',
          { className: 'row-message' },
          _react2.default.createElement(_MessageGroup.MessageGroup, {
            type: 'warning',
            title: 'There is fatal error in validation',
            expandText: 'Error details',
            messages: [error.message]
          })
        ),
        report && location.search && _react2.default.createElement(
          'div',
          { className: 'row-message' },
          _react2.default.createElement(
            'div',
            { className: 'alert alert-info' },
            _react2.default.createElement(
              'strong',
              null,
              'Permalink:'
            ),
            '\xA0',
            _react2.default.createElement(
              'a',
              { href: location.href },
              location.href
            )
          )
        ),
        report && _react2.default.createElement(
          'div',
          { className: 'row-report' },
          _react2.default.createElement(_Report.Report, { report: report })
        )
      );
    }

    // Private

  }, {
    key: 'onSourceTypeChange',
    value: function onSourceTypeChange() {
      this.setState({ isSourceFile: !this.state.isSourceFile });
      this.onSourceChange('');
    }
  }, {
    key: 'onSchemaTypeChange',
    value: function onSchemaTypeChange() {
      this.setState({ isSchemaFile: !this.state.isSchemaFile });
      this.onOptionsChange('schema', '');
    }
  }, {
    key: 'onSourceChange',
    value: function onSourceChange(value) {
      this.setState({ source: value });
    }
  }, {
    key: 'onOptionsChange',
    value: function onOptionsChange(key, value) {
      var options = (0, _helpers.merge)(this.state.options, _defineProperty({}, key, value));
      if (!value) delete options[key];
      this.setState({ options: options });
    }
  }, {
    key: 'onSubmit',
    value: function onSubmit() {
      var _this2 = this;

      var validate = this.props.validate;
      var _state3 = this.state,
          source = _state3.source,
          options = _state3.options;

      this.setState({ report: null, error: null, isLoading: true });
      validate(source, (0, _helpers.merge)(options)).then(function (report) {
        _this2.setState({ report: report, isLoading: false });
      }).catch(function (error) {
        _this2.setState({ error: error, isLoading: false });
      });
    }
  }]);

  return Form;
}(_react2.default.Component);

/***/ }),
/* 9 */
/* no static exports found */
/* all exports used */
/*!***********************!*\
  !*** ./src/render.js ***!
  \***********************/
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.render = render;

var _react = __webpack_require__(/*! react */ 0);

var _react2 = _interopRequireDefault(_react);

var _reactDom = __webpack_require__(/*! react-dom */ 0);

var _reactDom2 = _interopRequireDefault(_reactDom);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

// Module API

function render(component, props, element) {
  _reactDom2.default.render(_react2.default.createElement(component, props, null), element);
}

/***/ }),
/* 10 */
/* no static exports found */
/* all exports used */
/*!************************!*\
  !*** ./src/styles.css ***!
  \************************/
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),
/* 11 */
/* no static exports found */
/* all exports used */
/*!**************************************!*\
  !*** ./src/components/ErrorGroup.js ***!
  \**************************************/
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ErrorGroup = undefined;

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(/*! react */ 0);

var _react2 = _interopRequireDefault(_react);

var _marked = __webpack_require__(/*! marked */ 42);

var _marked2 = _interopRequireDefault(_marked);

var _classnames = __webpack_require__(/*! classnames */ 14);

var _classnames2 = _interopRequireDefault(_classnames);

var _startCase = __webpack_require__(/*! lodash/startCase */ 39);

var _startCase2 = _interopRequireDefault(_startCase);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var spec = __webpack_require__(/*! ../spec.json */ 43);

// Module API

var ErrorGroup = exports.ErrorGroup = function (_React$Component) {
  _inherits(ErrorGroup, _React$Component);

  // Public

  function ErrorGroup(_ref) {
    var errorGroup = _ref.errorGroup;

    _classCallCheck(this, ErrorGroup);

    var _this = _possibleConstructorReturn(this, (ErrorGroup.__proto__ || Object.getPrototypeOf(ErrorGroup)).call(this, { errorGroup: errorGroup }));

    _this.state = {
      showErrorDetails: false,
      visibleRowsCount: 10
    };
    return _this;
  }

  _createClass(ErrorGroup, [{
    key: 'render',
    value: function render() {
      var _this2 = this;

      var errorGroup = this.props.errorGroup;
      var _state = this.state,
          showErrorDetails = _state.showErrorDetails,
          visibleRowsCount = _state.visibleRowsCount;

      var errorDetails = getErrorDetails(errorGroup);
      var showHeaders = getShowHeaders(errorDetails);
      var description = getDescription(errorDetails);
      var rowNumbers = getRowNumbers(errorGroup);
      return _react2.default.createElement(
        'div',
        { className: 'result panel panel-danger' },
        _react2.default.createElement(
          'div',
          { className: 'panel-heading' },
          _react2.default.createElement(
            'span',
            { className: 'text-uppercase label label-danger' },
            'Invalid'
          ),
          _react2.default.createElement(
            'span',
            { className: 'text-uppercase label label-info' },
            errorDetails.type
          ),
          _react2.default.createElement(
            'span',
            { className: 'count label' },
            errorGroup.count
          ),
          _react2.default.createElement(
            'h5',
            { className: 'panel-title' },
            _react2.default.createElement(
              'a',
              { onClick: function onClick() {
                  return _this2.setState({ showErrorDetails: !showErrorDetails });
                } },
              errorDetails.name
            )
          ),
          _react2.default.createElement(
            'a',
            { className: 'error-details-link', onClick: function onClick() {
                return _this2.setState({ showErrorDetails: !showErrorDetails });
              } },
            'Error details'
          )
        ),
        showErrorDetails && description && _react2.default.createElement(
          'div',
          { className: 'panel-heading error-details' },
          _react2.default.createElement(
            'p',
            null,
            _react2.default.createElement('div', { dangerouslySetInnerHTML: { __html: description } })
          )
        ),
        showErrorDetails && _react2.default.createElement(
          'div',
          { className: 'panel-heading error-details' },
          _react2.default.createElement(
            'p',
            null,
            'The full list of error messages:'
          ),
          _react2.default.createElement(
            'ul',
            null,
            errorGroup.messages.map(function (message) {
              return _react2.default.createElement(
                'li',
                null,
                message
              );
            })
          )
        ),
        _react2.default.createElement(
          'div',
          { className: 'panel-body' },
          _react2.default.createElement(
            'div',
            { className: 'table-container' },
            _react2.default.createElement(
              'table',
              { className: 'table table-bordered table-condensed' },
              errorGroup.headers && showHeaders && _react2.default.createElement(ErrorGroupTableHead, { headers: errorGroup.headers }),
              _react2.default.createElement(ErrorGroupTableBody, {
                errorGroup: errorGroup,
                visibleRowsCount: visibleRowsCount,
                rowNumbers: rowNumbers
              })
            )
          ),
          visibleRowsCount < rowNumbers.length && _react2.default.createElement(
            'div',
            { className: 'show-more' },
            _react2.default.createElement(
              'a',
              { onClick: function onClick() {
                  _this2.setState({ visibleRowsCount: visibleRowsCount + 10 });
                } },
              'Show next 10 rows'
            )
          )
        )
      );
    }
  }]);

  return ErrorGroup;
}(_react2.default.Component);

// Internal

function ErrorGroupTableHead(_ref2) {
  var headers = _ref2.headers;

  return _react2.default.createElement(
    'thead',
    null,
    _react2.default.createElement(
      'tr',
      null,
      _react2.default.createElement('th', null),
      headers.map(function (header) {
        return _react2.default.createElement(
          'th',
          null,
          header
        );
      })
    )
  );
}

function ErrorGroupTableBody(_ref3) {
  var errorGroup = _ref3.errorGroup,
      visibleRowsCount = _ref3.visibleRowsCount,
      rowNumbers = _ref3.rowNumbers;

  return _react2.default.createElement(
    'tbody',
    null,
    rowNumbers.map(function (rowNumber, index) {
      return index < visibleRowsCount && _react2.default.createElement(
        'tr',
        { className: 'result-header-row' },
        rowNumber !== null && _react2.default.createElement(
          'td',
          { className: 'result-row-index' },
          rowNumber
        ),
        errorGroup.rows[rowNumber].values.map(function (value, innerIndex) {
          return _react2.default.createElement(
            'td',
            { className: (0, _classnames2.default)({ danger: errorGroup.rows[rowNumber].badcols.has(innerIndex + 1) }) },
            value
          );
        })
      );
    })
  );
}

function getErrorDetails(errorGroup) {

  // Get code handling legacy codes
  var code = errorGroup.code;
  if (code === 'non-castable-value') {
    code = 'type-or-format-error';
  }

  // Get details handling custom errors
  var details = spec.errors[code];
  if (!details) details = {
    name: (0, _startCase2.default)(code),
    type: 'custom',
    context: 'body',
    description: null
  };

  return details;
}

function getShowHeaders(errorDetails) {
  return errorDetails.context === 'body';
}

function getDescription(errorDetails) {
  var description = errorDetails.description;
  if (description) {
    description = description.replace('{validator}', '`goodtables.yml`');
    description = (0, _marked2.default)(description);
  }
  return description;
}

function getRowNumbers(errorGroup) {
  return Object.keys(errorGroup.rows).map(function (item) {
    return parseInt(item, 10) || null;
  }).sort(function (a, b) {
    return a - b;
  });
}

/***/ }),
/* 12 */
/* no static exports found */
/* all exports used */
/*!****************************************!*\
  !*** ./src/components/InvalidTable.js ***!
  \****************************************/
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

function _objectValues(obj) {
  var values = [];
  var keys = Object.keys(obj);

  for (var k = 0; k < keys.length; ++k) values.push(obj[keys[k]]);

  return values;
}

exports.InvalidTable = InvalidTable;

var _react = __webpack_require__(/*! react */ 0);

var _react2 = _interopRequireDefault(_react);

var _ErrorGroup = __webpack_require__(/*! ./ErrorGroup */ 11);

var _helpers = __webpack_require__(/*! ../helpers */ 1);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

// Module API

function InvalidTable(_ref) {
  var table = _ref.table,
      tableNumber = _ref.tableNumber,
      tablesCount = _ref.tablesCount;

  var errorGroups = (0, _helpers.getTableErrorGroups)(table);
  var tableFile = (0, _helpers.removeBaseUrl)(table.source);
  return _react2.default.createElement(
    'div',
    { className: 'report-table' },
    _react2.default.createElement(
      'h4',
      { className: 'file-heading' },
      _react2.default.createElement(
        'span',
        null,
        _react2.default.createElement(
          'a',
          { className: 'file-name', href: table.source },
          tableFile
        ),
        _react2.default.createElement(
          'span',
          { className: 'file-count' },
          'Invalid ',
          tableNumber,
          ' of ',
          tablesCount
        )
      )
    ),
    _objectValues(errorGroups).map(function (errorGroup) {
      return _react2.default.createElement(_ErrorGroup.ErrorGroup, { key: errorGroup.code, errorGroup: errorGroup });
    })
  );
}

/***/ }),
/* 13 */
/* no static exports found */
/* all exports used */
/*!**********************!*\
  !*** ./src/index.js ***!
  \**********************/
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.Form = exports.Report = exports.render = undefined;

__webpack_require__(/*! ./styles.css */ 10);

var _render = __webpack_require__(/*! ./render */ 9);

var _Report = __webpack_require__(/*! ./components/Report */ 4);

var _Form = __webpack_require__(/*! ./components/Form */ 8);

// Module API

exports.default = { render: _render.render, Report: _Report.Report, Form: _Form.Form };
exports.render = _render.render;
exports.Report = _Report.Report;
exports.Form = _Form.Form;

/***/ }),
/* 14 */
/* no static exports found */
/* all exports used */
/*!*******************************!*\
  !*** ./~/classnames/index.js ***!
  \*******************************/
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/*!
  Copyright (c) 2016 Jed Watson.
  Licensed under the MIT License (MIT), see
  http://jedwatson.github.io/classnames
*/
/* global define */

(function () {
	'use strict';

	var hasOwn = {}.hasOwnProperty;

	function classNames () {
		var classes = [];

		for (var i = 0; i < arguments.length; i++) {
			var arg = arguments[i];
			if (!arg) continue;

			var argType = typeof arg;

			if (argType === 'string' || argType === 'number') {
				classes.push(arg);
			} else if (Array.isArray(arg)) {
				classes.push(classNames.apply(null, arg));
			} else if (argType === 'object') {
				for (var key in arg) {
					if (hasOwn.call(arg, key) && arg[key]) {
						classes.push(key);
					}
				}
			}
		}

		return classes.join(' ');
	}

	if (typeof module !== 'undefined' && module.exports) {
		module.exports = classNames;
	} else if (true) {
		// register as 'classnames', consistent with npm package name
		!(__WEBPACK_AMD_DEFINE_ARRAY__ = [], __WEBPACK_AMD_DEFINE_RESULT__ = function () {
			return classNames;
		}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
	} else {
		window.classNames = classNames;
	}
}());


/***/ }),
/* 15 */
/* no static exports found */
/* all exports used */
/*!*******************************!*\
  !*** ./~/lodash/_arrayMap.js ***!
  \*******************************/
/***/ (function(module, exports) {

/**
 * A specialized version of `_.map` for arrays without support for iteratee
 * shorthands.
 *
 * @private
 * @param {Array} [array] The array to iterate over.
 * @param {Function} iteratee The function invoked per iteration.
 * @returns {Array} Returns the new mapped array.
 */
function arrayMap(array, iteratee) {
  var index = -1,
      length = array == null ? 0 : array.length,
      result = Array(length);

  while (++index < length) {
    result[index] = iteratee(array[index], index, array);
  }
  return result;
}

module.exports = arrayMap;


/***/ }),
/* 16 */
/* no static exports found */
/* all exports used */
/*!**********************************!*\
  !*** ./~/lodash/_arrayReduce.js ***!
  \**********************************/
/***/ (function(module, exports) {

/**
 * A specialized version of `_.reduce` for arrays without support for
 * iteratee shorthands.
 *
 * @private
 * @param {Array} [array] The array to iterate over.
 * @param {Function} iteratee The function invoked per iteration.
 * @param {*} [accumulator] The initial value.
 * @param {boolean} [initAccum] Specify using the first element of `array` as
 *  the initial value.
 * @returns {*} Returns the accumulated value.
 */
function arrayReduce(array, iteratee, accumulator, initAccum) {
  var index = -1,
      length = array == null ? 0 : array.length;

  if (initAccum && length) {
    accumulator = array[++index];
  }
  while (++index < length) {
    accumulator = iteratee(accumulator, array[index], index, array);
  }
  return accumulator;
}

module.exports = arrayReduce;


/***/ }),
/* 17 */
/* no static exports found */
/* all exports used */
/*!***********************************!*\
  !*** ./~/lodash/_asciiToArray.js ***!
  \***********************************/
/***/ (function(module, exports) {

/**
 * Converts an ASCII `string` to an array.
 *
 * @private
 * @param {string} string The string to convert.
 * @returns {Array} Returns the converted array.
 */
function asciiToArray(string) {
  return string.split('');
}

module.exports = asciiToArray;


/***/ }),
/* 18 */
/* no static exports found */
/* all exports used */
/*!*********************************!*\
  !*** ./~/lodash/_asciiWords.js ***!
  \*********************************/
/***/ (function(module, exports) {

/** Used to match words composed of alphanumeric characters. */
var reAsciiWord = /[^\x00-\x2f\x3a-\x40\x5b-\x60\x7b-\x7f]+/g;

/**
 * Splits an ASCII `string` into an array of its words.
 *
 * @private
 * @param {string} The string to inspect.
 * @returns {Array} Returns the words of `string`.
 */
function asciiWords(string) {
  return string.match(reAsciiWord) || [];
}

module.exports = asciiWords;


/***/ }),
/* 19 */
/* no static exports found */
/* all exports used */
/*!*********************************!*\
  !*** ./~/lodash/_baseGetTag.js ***!
  \*********************************/
/***/ (function(module, exports, __webpack_require__) {

var Symbol = __webpack_require__(/*! ./_Symbol */ 2),
    getRawTag = __webpack_require__(/*! ./_getRawTag */ 28),
    objectToString = __webpack_require__(/*! ./_objectToString */ 30);

/** `Object#toString` result references. */
var nullTag = '[object Null]',
    undefinedTag = '[object Undefined]';

/** Built-in value references. */
var symToStringTag = Symbol ? Symbol.toStringTag : undefined;

/**
 * The base implementation of `getTag` without fallbacks for buggy environments.
 *
 * @private
 * @param {*} value The value to query.
 * @returns {string} Returns the `toStringTag`.
 */
function baseGetTag(value) {
  if (value == null) {
    return value === undefined ? undefinedTag : nullTag;
  }
  return (symToStringTag && symToStringTag in Object(value))
    ? getRawTag(value)
    : objectToString(value);
}

module.exports = baseGetTag;


/***/ }),
/* 20 */
/* no static exports found */
/* all exports used */
/*!*************************************!*\
  !*** ./~/lodash/_basePropertyOf.js ***!
  \*************************************/
/***/ (function(module, exports) {

/**
 * The base implementation of `_.propertyOf` without support for deep paths.
 *
 * @private
 * @param {Object} object The object to query.
 * @returns {Function} Returns the new accessor function.
 */
function basePropertyOf(object) {
  return function(key) {
    return object == null ? undefined : object[key];
  };
}

module.exports = basePropertyOf;


/***/ }),
/* 21 */
/* no static exports found */
/* all exports used */
/*!********************************!*\
  !*** ./~/lodash/_baseSlice.js ***!
  \********************************/
/***/ (function(module, exports) {

/**
 * The base implementation of `_.slice` without an iteratee call guard.
 *
 * @private
 * @param {Array} array The array to slice.
 * @param {number} [start=0] The start position.
 * @param {number} [end=array.length] The end position.
 * @returns {Array} Returns the slice of `array`.
 */
function baseSlice(array, start, end) {
  var index = -1,
      length = array.length;

  if (start < 0) {
    start = -start > length ? 0 : (length + start);
  }
  end = end > length ? length : end;
  if (end < 0) {
    end += length;
  }
  length = start > end ? 0 : ((end - start) >>> 0);
  start >>>= 0;

  var result = Array(length);
  while (++index < length) {
    result[index] = array[index + start];
  }
  return result;
}

module.exports = baseSlice;


/***/ }),
/* 22 */
/* no static exports found */
/* all exports used */
/*!***********************************!*\
  !*** ./~/lodash/_baseToString.js ***!
  \***********************************/
/***/ (function(module, exports, __webpack_require__) {

var Symbol = __webpack_require__(/*! ./_Symbol */ 2),
    arrayMap = __webpack_require__(/*! ./_arrayMap */ 15),
    isArray = __webpack_require__(/*! ./isArray */ 36),
    isSymbol = __webpack_require__(/*! ./isSymbol */ 38);

/** Used as references for various `Number` constants. */
var INFINITY = 1 / 0;

/** Used to convert symbols to primitives and strings. */
var symbolProto = Symbol ? Symbol.prototype : undefined,
    symbolToString = symbolProto ? symbolProto.toString : undefined;

/**
 * The base implementation of `_.toString` which doesn't convert nullish
 * values to empty strings.
 *
 * @private
 * @param {*} value The value to process.
 * @returns {string} Returns the string.
 */
function baseToString(value) {
  // Exit early for strings to avoid a performance hit in some environments.
  if (typeof value == 'string') {
    return value;
  }
  if (isArray(value)) {
    // Recursively convert values (susceptible to call stack limits).
    return arrayMap(value, baseToString) + '';
  }
  if (isSymbol(value)) {
    return symbolToString ? symbolToString.call(value) : '';
  }
  var result = (value + '');
  return (result == '0' && (1 / value) == -INFINITY) ? '-0' : result;
}

module.exports = baseToString;


/***/ }),
/* 23 */
/* no static exports found */
/* all exports used */
/*!********************************!*\
  !*** ./~/lodash/_castSlice.js ***!
  \********************************/
/***/ (function(module, exports, __webpack_require__) {

var baseSlice = __webpack_require__(/*! ./_baseSlice */ 21);

/**
 * Casts `array` to a slice if it's needed.
 *
 * @private
 * @param {Array} array The array to inspect.
 * @param {number} start The start position.
 * @param {number} [end=array.length] The end position.
 * @returns {Array} Returns the cast slice.
 */
function castSlice(array, start, end) {
  var length = array.length;
  end = end === undefined ? length : end;
  return (!start && end >= length) ? array : baseSlice(array, start, end);
}

module.exports = castSlice;


/***/ }),
/* 24 */
/* no static exports found */
/* all exports used */
/*!**************************************!*\
  !*** ./~/lodash/_createCaseFirst.js ***!
  \**************************************/
/***/ (function(module, exports, __webpack_require__) {

var castSlice = __webpack_require__(/*! ./_castSlice */ 23),
    hasUnicode = __webpack_require__(/*! ./_hasUnicode */ 6),
    stringToArray = __webpack_require__(/*! ./_stringToArray */ 32),
    toString = __webpack_require__(/*! ./toString */ 3);

/**
 * Creates a function like `_.lowerFirst`.
 *
 * @private
 * @param {string} methodName The name of the `String` case method to use.
 * @returns {Function} Returns the new case function.
 */
function createCaseFirst(methodName) {
  return function(string) {
    string = toString(string);

    var strSymbols = hasUnicode(string)
      ? stringToArray(string)
      : undefined;

    var chr = strSymbols
      ? strSymbols[0]
      : string.charAt(0);

    var trailing = strSymbols
      ? castSlice(strSymbols, 1).join('')
      : string.slice(1);

    return chr[methodName]() + trailing;
  };
}

module.exports = createCaseFirst;


/***/ }),
/* 25 */
/* no static exports found */
/* all exports used */
/*!***************************************!*\
  !*** ./~/lodash/_createCompounder.js ***!
  \***************************************/
/***/ (function(module, exports, __webpack_require__) {

var arrayReduce = __webpack_require__(/*! ./_arrayReduce */ 16),
    deburr = __webpack_require__(/*! ./deburr */ 35),
    words = __webpack_require__(/*! ./words */ 41);

/** Used to compose unicode capture groups. */
var rsApos = "['\u2019]";

/** Used to match apostrophes. */
var reApos = RegExp(rsApos, 'g');

/**
 * Creates a function like `_.camelCase`.
 *
 * @private
 * @param {Function} callback The function to combine each word.
 * @returns {Function} Returns the new compounder function.
 */
function createCompounder(callback) {
  return function(string) {
    return arrayReduce(words(deburr(string).replace(reApos, '')), callback, '');
  };
}

module.exports = createCompounder;


/***/ }),
/* 26 */
/* no static exports found */
/* all exports used */
/*!***********************************!*\
  !*** ./~/lodash/_deburrLetter.js ***!
  \***********************************/
/***/ (function(module, exports, __webpack_require__) {

var basePropertyOf = __webpack_require__(/*! ./_basePropertyOf */ 20);

/** Used to map Latin Unicode letters to basic Latin letters. */
var deburredLetters = {
  // Latin-1 Supplement block.
  '\xc0': 'A',  '\xc1': 'A', '\xc2': 'A', '\xc3': 'A', '\xc4': 'A', '\xc5': 'A',
  '\xe0': 'a',  '\xe1': 'a', '\xe2': 'a', '\xe3': 'a', '\xe4': 'a', '\xe5': 'a',
  '\xc7': 'C',  '\xe7': 'c',
  '\xd0': 'D',  '\xf0': 'd',
  '\xc8': 'E',  '\xc9': 'E', '\xca': 'E', '\xcb': 'E',
  '\xe8': 'e',  '\xe9': 'e', '\xea': 'e', '\xeb': 'e',
  '\xcc': 'I',  '\xcd': 'I', '\xce': 'I', '\xcf': 'I',
  '\xec': 'i',  '\xed': 'i', '\xee': 'i', '\xef': 'i',
  '\xd1': 'N',  '\xf1': 'n',
  '\xd2': 'O',  '\xd3': 'O', '\xd4': 'O', '\xd5': 'O', '\xd6': 'O', '\xd8': 'O',
  '\xf2': 'o',  '\xf3': 'o', '\xf4': 'o', '\xf5': 'o', '\xf6': 'o', '\xf8': 'o',
  '\xd9': 'U',  '\xda': 'U', '\xdb': 'U', '\xdc': 'U',
  '\xf9': 'u',  '\xfa': 'u', '\xfb': 'u', '\xfc': 'u',
  '\xdd': 'Y',  '\xfd': 'y', '\xff': 'y',
  '\xc6': 'Ae', '\xe6': 'ae',
  '\xde': 'Th', '\xfe': 'th',
  '\xdf': 'ss',
  // Latin Extended-A block.
  '\u0100': 'A',  '\u0102': 'A', '\u0104': 'A',
  '\u0101': 'a',  '\u0103': 'a', '\u0105': 'a',
  '\u0106': 'C',  '\u0108': 'C', '\u010a': 'C', '\u010c': 'C',
  '\u0107': 'c',  '\u0109': 'c', '\u010b': 'c', '\u010d': 'c',
  '\u010e': 'D',  '\u0110': 'D', '\u010f': 'd', '\u0111': 'd',
  '\u0112': 'E',  '\u0114': 'E', '\u0116': 'E', '\u0118': 'E', '\u011a': 'E',
  '\u0113': 'e',  '\u0115': 'e', '\u0117': 'e', '\u0119': 'e', '\u011b': 'e',
  '\u011c': 'G',  '\u011e': 'G', '\u0120': 'G', '\u0122': 'G',
  '\u011d': 'g',  '\u011f': 'g', '\u0121': 'g', '\u0123': 'g',
  '\u0124': 'H',  '\u0126': 'H', '\u0125': 'h', '\u0127': 'h',
  '\u0128': 'I',  '\u012a': 'I', '\u012c': 'I', '\u012e': 'I', '\u0130': 'I',
  '\u0129': 'i',  '\u012b': 'i', '\u012d': 'i', '\u012f': 'i', '\u0131': 'i',
  '\u0134': 'J',  '\u0135': 'j',
  '\u0136': 'K',  '\u0137': 'k', '\u0138': 'k',
  '\u0139': 'L',  '\u013b': 'L', '\u013d': 'L', '\u013f': 'L', '\u0141': 'L',
  '\u013a': 'l',  '\u013c': 'l', '\u013e': 'l', '\u0140': 'l', '\u0142': 'l',
  '\u0143': 'N',  '\u0145': 'N', '\u0147': 'N', '\u014a': 'N',
  '\u0144': 'n',  '\u0146': 'n', '\u0148': 'n', '\u014b': 'n',
  '\u014c': 'O',  '\u014e': 'O', '\u0150': 'O',
  '\u014d': 'o',  '\u014f': 'o', '\u0151': 'o',
  '\u0154': 'R',  '\u0156': 'R', '\u0158': 'R',
  '\u0155': 'r',  '\u0157': 'r', '\u0159': 'r',
  '\u015a': 'S',  '\u015c': 'S', '\u015e': 'S', '\u0160': 'S',
  '\u015b': 's',  '\u015d': 's', '\u015f': 's', '\u0161': 's',
  '\u0162': 'T',  '\u0164': 'T', '\u0166': 'T',
  '\u0163': 't',  '\u0165': 't', '\u0167': 't',
  '\u0168': 'U',  '\u016a': 'U', '\u016c': 'U', '\u016e': 'U', '\u0170': 'U', '\u0172': 'U',
  '\u0169': 'u',  '\u016b': 'u', '\u016d': 'u', '\u016f': 'u', '\u0171': 'u', '\u0173': 'u',
  '\u0174': 'W',  '\u0175': 'w',
  '\u0176': 'Y',  '\u0177': 'y', '\u0178': 'Y',
  '\u0179': 'Z',  '\u017b': 'Z', '\u017d': 'Z',
  '\u017a': 'z',  '\u017c': 'z', '\u017e': 'z',
  '\u0132': 'IJ', '\u0133': 'ij',
  '\u0152': 'Oe', '\u0153': 'oe',
  '\u0149': "'n", '\u017f': 's'
};

/**
 * Used by `_.deburr` to convert Latin-1 Supplement and Latin Extended-A
 * letters to basic Latin letters.
 *
 * @private
 * @param {string} letter The matched letter to deburr.
 * @returns {string} Returns the deburred letter.
 */
var deburrLetter = basePropertyOf(deburredLetters);

module.exports = deburrLetter;


/***/ }),
/* 27 */
/* no static exports found */
/* all exports used */
/*!*********************************!*\
  !*** ./~/lodash/_freeGlobal.js ***!
  \*********************************/
/***/ (function(module, exports, __webpack_require__) {

/* WEBPACK VAR INJECTION */(function(global) {/** Detect free variable `global` from Node.js. */
var freeGlobal = typeof global == 'object' && global && global.Object === Object && global;

module.exports = freeGlobal;

/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(/*! ./../webpack/buildin/global.js */ 7)))

/***/ }),
/* 28 */
/* no static exports found */
/* all exports used */
/*!********************************!*\
  !*** ./~/lodash/_getRawTag.js ***!
  \********************************/
/***/ (function(module, exports, __webpack_require__) {

var Symbol = __webpack_require__(/*! ./_Symbol */ 2);

/** Used for built-in method references. */
var objectProto = Object.prototype;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/**
 * Used to resolve the
 * [`toStringTag`](http://ecma-international.org/ecma-262/7.0/#sec-object.prototype.tostring)
 * of values.
 */
var nativeObjectToString = objectProto.toString;

/** Built-in value references. */
var symToStringTag = Symbol ? Symbol.toStringTag : undefined;

/**
 * A specialized version of `baseGetTag` which ignores `Symbol.toStringTag` values.
 *
 * @private
 * @param {*} value The value to query.
 * @returns {string} Returns the raw `toStringTag`.
 */
function getRawTag(value) {
  var isOwn = hasOwnProperty.call(value, symToStringTag),
      tag = value[symToStringTag];

  try {
    value[symToStringTag] = undefined;
    var unmasked = true;
  } catch (e) {}

  var result = nativeObjectToString.call(value);
  if (unmasked) {
    if (isOwn) {
      value[symToStringTag] = tag;
    } else {
      delete value[symToStringTag];
    }
  }
  return result;
}

module.exports = getRawTag;


/***/ }),
/* 29 */
/* no static exports found */
/* all exports used */
/*!*************************************!*\
  !*** ./~/lodash/_hasUnicodeWord.js ***!
  \*************************************/
/***/ (function(module, exports) {

/** Used to detect strings that need a more robust regexp to match words. */
var reHasUnicodeWord = /[a-z][A-Z]|[A-Z]{2,}[a-z]|[0-9][a-zA-Z]|[a-zA-Z][0-9]|[^a-zA-Z0-9 ]/;

/**
 * Checks if `string` contains a word composed of Unicode symbols.
 *
 * @private
 * @param {string} string The string to inspect.
 * @returns {boolean} Returns `true` if a word is found, else `false`.
 */
function hasUnicodeWord(string) {
  return reHasUnicodeWord.test(string);
}

module.exports = hasUnicodeWord;


/***/ }),
/* 30 */
/* no static exports found */
/* all exports used */
/*!*************************************!*\
  !*** ./~/lodash/_objectToString.js ***!
  \*************************************/
/***/ (function(module, exports) {

/** Used for built-in method references. */
var objectProto = Object.prototype;

/**
 * Used to resolve the
 * [`toStringTag`](http://ecma-international.org/ecma-262/7.0/#sec-object.prototype.tostring)
 * of values.
 */
var nativeObjectToString = objectProto.toString;

/**
 * Converts `value` to a string using `Object.prototype.toString`.
 *
 * @private
 * @param {*} value The value to convert.
 * @returns {string} Returns the converted string.
 */
function objectToString(value) {
  return nativeObjectToString.call(value);
}

module.exports = objectToString;


/***/ }),
/* 31 */
/* no static exports found */
/* all exports used */
/*!***************************!*\
  !*** ./~/lodash/_root.js ***!
  \***************************/
/***/ (function(module, exports, __webpack_require__) {

var freeGlobal = __webpack_require__(/*! ./_freeGlobal */ 27);

/** Detect free variable `self`. */
var freeSelf = typeof self == 'object' && self && self.Object === Object && self;

/** Used as a reference to the global object. */
var root = freeGlobal || freeSelf || Function('return this')();

module.exports = root;


/***/ }),
/* 32 */
/* no static exports found */
/* all exports used */
/*!************************************!*\
  !*** ./~/lodash/_stringToArray.js ***!
  \************************************/
/***/ (function(module, exports, __webpack_require__) {

var asciiToArray = __webpack_require__(/*! ./_asciiToArray */ 17),
    hasUnicode = __webpack_require__(/*! ./_hasUnicode */ 6),
    unicodeToArray = __webpack_require__(/*! ./_unicodeToArray */ 33);

/**
 * Converts `string` to an array.
 *
 * @private
 * @param {string} string The string to convert.
 * @returns {Array} Returns the converted array.
 */
function stringToArray(string) {
  return hasUnicode(string)
    ? unicodeToArray(string)
    : asciiToArray(string);
}

module.exports = stringToArray;


/***/ }),
/* 33 */
/* no static exports found */
/* all exports used */
/*!*************************************!*\
  !*** ./~/lodash/_unicodeToArray.js ***!
  \*************************************/
/***/ (function(module, exports) {

/** Used to compose unicode character classes. */
var rsAstralRange = '\\ud800-\\udfff',
    rsComboMarksRange = '\\u0300-\\u036f',
    reComboHalfMarksRange = '\\ufe20-\\ufe2f',
    rsComboSymbolsRange = '\\u20d0-\\u20ff',
    rsComboRange = rsComboMarksRange + reComboHalfMarksRange + rsComboSymbolsRange,
    rsVarRange = '\\ufe0e\\ufe0f';

/** Used to compose unicode capture groups. */
var rsAstral = '[' + rsAstralRange + ']',
    rsCombo = '[' + rsComboRange + ']',
    rsFitz = '\\ud83c[\\udffb-\\udfff]',
    rsModifier = '(?:' + rsCombo + '|' + rsFitz + ')',
    rsNonAstral = '[^' + rsAstralRange + ']',
    rsRegional = '(?:\\ud83c[\\udde6-\\uddff]){2}',
    rsSurrPair = '[\\ud800-\\udbff][\\udc00-\\udfff]',
    rsZWJ = '\\u200d';

/** Used to compose unicode regexes. */
var reOptMod = rsModifier + '?',
    rsOptVar = '[' + rsVarRange + ']?',
    rsOptJoin = '(?:' + rsZWJ + '(?:' + [rsNonAstral, rsRegional, rsSurrPair].join('|') + ')' + rsOptVar + reOptMod + ')*',
    rsSeq = rsOptVar + reOptMod + rsOptJoin,
    rsSymbol = '(?:' + [rsNonAstral + rsCombo + '?', rsCombo, rsRegional, rsSurrPair, rsAstral].join('|') + ')';

/** Used to match [string symbols](https://mathiasbynens.be/notes/javascript-unicode). */
var reUnicode = RegExp(rsFitz + '(?=' + rsFitz + ')|' + rsSymbol + rsSeq, 'g');

/**
 * Converts a Unicode `string` to an array.
 *
 * @private
 * @param {string} string The string to convert.
 * @returns {Array} Returns the converted array.
 */
function unicodeToArray(string) {
  return string.match(reUnicode) || [];
}

module.exports = unicodeToArray;


/***/ }),
/* 34 */
/* no static exports found */
/* all exports used */
/*!***********************************!*\
  !*** ./~/lodash/_unicodeWords.js ***!
  \***********************************/
/***/ (function(module, exports) {

/** Used to compose unicode character classes. */
var rsAstralRange = '\\ud800-\\udfff',
    rsComboMarksRange = '\\u0300-\\u036f',
    reComboHalfMarksRange = '\\ufe20-\\ufe2f',
    rsComboSymbolsRange = '\\u20d0-\\u20ff',
    rsComboRange = rsComboMarksRange + reComboHalfMarksRange + rsComboSymbolsRange,
    rsDingbatRange = '\\u2700-\\u27bf',
    rsLowerRange = 'a-z\\xdf-\\xf6\\xf8-\\xff',
    rsMathOpRange = '\\xac\\xb1\\xd7\\xf7',
    rsNonCharRange = '\\x00-\\x2f\\x3a-\\x40\\x5b-\\x60\\x7b-\\xbf',
    rsPunctuationRange = '\\u2000-\\u206f',
    rsSpaceRange = ' \\t\\x0b\\f\\xa0\\ufeff\\n\\r\\u2028\\u2029\\u1680\\u180e\\u2000\\u2001\\u2002\\u2003\\u2004\\u2005\\u2006\\u2007\\u2008\\u2009\\u200a\\u202f\\u205f\\u3000',
    rsUpperRange = 'A-Z\\xc0-\\xd6\\xd8-\\xde',
    rsVarRange = '\\ufe0e\\ufe0f',
    rsBreakRange = rsMathOpRange + rsNonCharRange + rsPunctuationRange + rsSpaceRange;

/** Used to compose unicode capture groups. */
var rsApos = "['\u2019]",
    rsBreak = '[' + rsBreakRange + ']',
    rsCombo = '[' + rsComboRange + ']',
    rsDigits = '\\d+',
    rsDingbat = '[' + rsDingbatRange + ']',
    rsLower = '[' + rsLowerRange + ']',
    rsMisc = '[^' + rsAstralRange + rsBreakRange + rsDigits + rsDingbatRange + rsLowerRange + rsUpperRange + ']',
    rsFitz = '\\ud83c[\\udffb-\\udfff]',
    rsModifier = '(?:' + rsCombo + '|' + rsFitz + ')',
    rsNonAstral = '[^' + rsAstralRange + ']',
    rsRegional = '(?:\\ud83c[\\udde6-\\uddff]){2}',
    rsSurrPair = '[\\ud800-\\udbff][\\udc00-\\udfff]',
    rsUpper = '[' + rsUpperRange + ']',
    rsZWJ = '\\u200d';

/** Used to compose unicode regexes. */
var rsMiscLower = '(?:' + rsLower + '|' + rsMisc + ')',
    rsMiscUpper = '(?:' + rsUpper + '|' + rsMisc + ')',
    rsOptContrLower = '(?:' + rsApos + '(?:d|ll|m|re|s|t|ve))?',
    rsOptContrUpper = '(?:' + rsApos + '(?:D|LL|M|RE|S|T|VE))?',
    reOptMod = rsModifier + '?',
    rsOptVar = '[' + rsVarRange + ']?',
    rsOptJoin = '(?:' + rsZWJ + '(?:' + [rsNonAstral, rsRegional, rsSurrPair].join('|') + ')' + rsOptVar + reOptMod + ')*',
    rsOrdLower = '\\d*(?:(?:1st|2nd|3rd|(?![123])\\dth)\\b)',
    rsOrdUpper = '\\d*(?:(?:1ST|2ND|3RD|(?![123])\\dTH)\\b)',
    rsSeq = rsOptVar + reOptMod + rsOptJoin,
    rsEmoji = '(?:' + [rsDingbat, rsRegional, rsSurrPair].join('|') + ')' + rsSeq;

/** Used to match complex or compound words. */
var reUnicodeWord = RegExp([
  rsUpper + '?' + rsLower + '+' + rsOptContrLower + '(?=' + [rsBreak, rsUpper, '$'].join('|') + ')',
  rsMiscUpper + '+' + rsOptContrUpper + '(?=' + [rsBreak, rsUpper + rsMiscLower, '$'].join('|') + ')',
  rsUpper + '?' + rsMiscLower + '+' + rsOptContrLower,
  rsUpper + '+' + rsOptContrUpper,
  rsOrdUpper,
  rsOrdLower,
  rsDigits,
  rsEmoji
].join('|'), 'g');

/**
 * Splits a Unicode `string` into an array of its words.
 *
 * @private
 * @param {string} The string to inspect.
 * @returns {Array} Returns the words of `string`.
 */
function unicodeWords(string) {
  return string.match(reUnicodeWord) || [];
}

module.exports = unicodeWords;


/***/ }),
/* 35 */
/* no static exports found */
/* all exports used */
/*!****************************!*\
  !*** ./~/lodash/deburr.js ***!
  \****************************/
/***/ (function(module, exports, __webpack_require__) {

var deburrLetter = __webpack_require__(/*! ./_deburrLetter */ 26),
    toString = __webpack_require__(/*! ./toString */ 3);

/** Used to match Latin Unicode letters (excluding mathematical operators). */
var reLatin = /[\xc0-\xd6\xd8-\xf6\xf8-\xff\u0100-\u017f]/g;

/** Used to compose unicode character classes. */
var rsComboMarksRange = '\\u0300-\\u036f',
    reComboHalfMarksRange = '\\ufe20-\\ufe2f',
    rsComboSymbolsRange = '\\u20d0-\\u20ff',
    rsComboRange = rsComboMarksRange + reComboHalfMarksRange + rsComboSymbolsRange;

/** Used to compose unicode capture groups. */
var rsCombo = '[' + rsComboRange + ']';

/**
 * Used to match [combining diacritical marks](https://en.wikipedia.org/wiki/Combining_Diacritical_Marks) and
 * [combining diacritical marks for symbols](https://en.wikipedia.org/wiki/Combining_Diacritical_Marks_for_Symbols).
 */
var reComboMark = RegExp(rsCombo, 'g');

/**
 * Deburrs `string` by converting
 * [Latin-1 Supplement](https://en.wikipedia.org/wiki/Latin-1_Supplement_(Unicode_block)#Character_table)
 * and [Latin Extended-A](https://en.wikipedia.org/wiki/Latin_Extended-A)
 * letters to basic Latin letters and removing
 * [combining diacritical marks](https://en.wikipedia.org/wiki/Combining_Diacritical_Marks).
 *
 * @static
 * @memberOf _
 * @since 3.0.0
 * @category String
 * @param {string} [string=''] The string to deburr.
 * @returns {string} Returns the deburred string.
 * @example
 *
 * _.deburr('déjà vu');
 * // => 'deja vu'
 */
function deburr(string) {
  string = toString(string);
  return string && string.replace(reLatin, deburrLetter).replace(reComboMark, '');
}

module.exports = deburr;


/***/ }),
/* 36 */
/* no static exports found */
/* all exports used */
/*!*****************************!*\
  !*** ./~/lodash/isArray.js ***!
  \*****************************/
/***/ (function(module, exports) {

/**
 * Checks if `value` is classified as an `Array` object.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is an array, else `false`.
 * @example
 *
 * _.isArray([1, 2, 3]);
 * // => true
 *
 * _.isArray(document.body.children);
 * // => false
 *
 * _.isArray('abc');
 * // => false
 *
 * _.isArray(_.noop);
 * // => false
 */
var isArray = Array.isArray;

module.exports = isArray;


/***/ }),
/* 37 */
/* no static exports found */
/* all exports used */
/*!**********************************!*\
  !*** ./~/lodash/isObjectLike.js ***!
  \**********************************/
/***/ (function(module, exports) {

/**
 * Checks if `value` is object-like. A value is object-like if it's not `null`
 * and has a `typeof` result of "object".
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is object-like, else `false`.
 * @example
 *
 * _.isObjectLike({});
 * // => true
 *
 * _.isObjectLike([1, 2, 3]);
 * // => true
 *
 * _.isObjectLike(_.noop);
 * // => false
 *
 * _.isObjectLike(null);
 * // => false
 */
function isObjectLike(value) {
  return value != null && typeof value == 'object';
}

module.exports = isObjectLike;


/***/ }),
/* 38 */
/* no static exports found */
/* all exports used */
/*!******************************!*\
  !*** ./~/lodash/isSymbol.js ***!
  \******************************/
/***/ (function(module, exports, __webpack_require__) {

var baseGetTag = __webpack_require__(/*! ./_baseGetTag */ 19),
    isObjectLike = __webpack_require__(/*! ./isObjectLike */ 37);

/** `Object#toString` result references. */
var symbolTag = '[object Symbol]';

/**
 * Checks if `value` is classified as a `Symbol` primitive or object.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a symbol, else `false`.
 * @example
 *
 * _.isSymbol(Symbol.iterator);
 * // => true
 *
 * _.isSymbol('abc');
 * // => false
 */
function isSymbol(value) {
  return typeof value == 'symbol' ||
    (isObjectLike(value) && baseGetTag(value) == symbolTag);
}

module.exports = isSymbol;


/***/ }),
/* 39 */
/* no static exports found */
/* all exports used */
/*!*******************************!*\
  !*** ./~/lodash/startCase.js ***!
  \*******************************/
/***/ (function(module, exports, __webpack_require__) {

var createCompounder = __webpack_require__(/*! ./_createCompounder */ 25),
    upperFirst = __webpack_require__(/*! ./upperFirst */ 40);

/**
 * Converts `string` to
 * [start case](https://en.wikipedia.org/wiki/Letter_case#Stylistic_or_specialised_usage).
 *
 * @static
 * @memberOf _
 * @since 3.1.0
 * @category String
 * @param {string} [string=''] The string to convert.
 * @returns {string} Returns the start cased string.
 * @example
 *
 * _.startCase('--foo-bar--');
 * // => 'Foo Bar'
 *
 * _.startCase('fooBar');
 * // => 'Foo Bar'
 *
 * _.startCase('__FOO_BAR__');
 * // => 'FOO BAR'
 */
var startCase = createCompounder(function(result, word, index) {
  return result + (index ? ' ' : '') + upperFirst(word);
});

module.exports = startCase;


/***/ }),
/* 40 */
/* no static exports found */
/* all exports used */
/*!********************************!*\
  !*** ./~/lodash/upperFirst.js ***!
  \********************************/
/***/ (function(module, exports, __webpack_require__) {

var createCaseFirst = __webpack_require__(/*! ./_createCaseFirst */ 24);

/**
 * Converts the first character of `string` to upper case.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category String
 * @param {string} [string=''] The string to convert.
 * @returns {string} Returns the converted string.
 * @example
 *
 * _.upperFirst('fred');
 * // => 'Fred'
 *
 * _.upperFirst('FRED');
 * // => 'FRED'
 */
var upperFirst = createCaseFirst('toUpperCase');

module.exports = upperFirst;


/***/ }),
/* 41 */
/* no static exports found */
/* all exports used */
/*!***************************!*\
  !*** ./~/lodash/words.js ***!
  \***************************/
/***/ (function(module, exports, __webpack_require__) {

var asciiWords = __webpack_require__(/*! ./_asciiWords */ 18),
    hasUnicodeWord = __webpack_require__(/*! ./_hasUnicodeWord */ 29),
    toString = __webpack_require__(/*! ./toString */ 3),
    unicodeWords = __webpack_require__(/*! ./_unicodeWords */ 34);

/**
 * Splits `string` into an array of its words.
 *
 * @static
 * @memberOf _
 * @since 3.0.0
 * @category String
 * @param {string} [string=''] The string to inspect.
 * @param {RegExp|string} [pattern] The pattern to match words.
 * @param- {Object} [guard] Enables use as an iteratee for methods like `_.map`.
 * @returns {Array} Returns the words of `string`.
 * @example
 *
 * _.words('fred, barney, & pebbles');
 * // => ['fred', 'barney', 'pebbles']
 *
 * _.words('fred, barney, & pebbles', /[^, ]+/g);
 * // => ['fred', 'barney', '&', 'pebbles']
 */
function words(string, pattern, guard) {
  string = toString(string);
  pattern = guard ? undefined : pattern;

  if (pattern === undefined) {
    return hasUnicodeWord(string) ? unicodeWords(string) : asciiWords(string);
  }
  return string.match(pattern) || [];
}

module.exports = words;


/***/ }),
/* 42 */
/* no static exports found */
/* all exports used */
/*!********************************!*\
  !*** ./~/marked/lib/marked.js ***!
  \********************************/
/***/ (function(module, exports, __webpack_require__) {

/* WEBPACK VAR INJECTION */(function(global) {/**
 * marked - a markdown parser
 * Copyright (c) 2011-2014, Christopher Jeffrey. (MIT Licensed)
 * https://github.com/chjj/marked
 */

;(function() {

/**
 * Block-Level Grammar
 */

var block = {
  newline: /^\n+/,
  code: /^( {4}[^\n]+\n*)+/,
  fences: noop,
  hr: /^( *[-*_]){3,} *(?:\n+|$)/,
  heading: /^ *(#{1,6}) *([^\n]+?) *#* *(?:\n+|$)/,
  nptable: noop,
  lheading: /^([^\n]+)\n *(=|-){2,} *(?:\n+|$)/,
  blockquote: /^( *>[^\n]+(\n(?!def)[^\n]+)*\n*)+/,
  list: /^( *)(bull) [\s\S]+?(?:hr|def|\n{2,}(?! )(?!\1bull )\n*|\s*$)/,
  html: /^ *(?:comment *(?:\n|\s*$)|closed *(?:\n{2,}|\s*$)|closing *(?:\n{2,}|\s*$))/,
  def: /^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +["(]([^\n]+)[")])? *(?:\n+|$)/,
  table: noop,
  paragraph: /^((?:[^\n]+\n?(?!hr|heading|lheading|blockquote|tag|def))+)\n*/,
  text: /^[^\n]+/
};

block.bullet = /(?:[*+-]|\d+\.)/;
block.item = /^( *)(bull) [^\n]*(?:\n(?!\1bull )[^\n]*)*/;
block.item = replace(block.item, 'gm')
  (/bull/g, block.bullet)
  ();

block.list = replace(block.list)
  (/bull/g, block.bullet)
  ('hr', '\\n+(?=\\1?(?:[-*_] *){3,}(?:\\n+|$))')
  ('def', '\\n+(?=' + block.def.source + ')')
  ();

block.blockquote = replace(block.blockquote)
  ('def', block.def)
  ();

block._tag = '(?!(?:'
  + 'a|em|strong|small|s|cite|q|dfn|abbr|data|time|code'
  + '|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo'
  + '|span|br|wbr|ins|del|img)\\b)\\w+(?!:/|[^\\w\\s@]*@)\\b';

block.html = replace(block.html)
  ('comment', /<!--[\s\S]*?-->/)
  ('closed', /<(tag)[\s\S]+?<\/\1>/)
  ('closing', /<tag(?:"[^"]*"|'[^']*'|[^'">])*?>/)
  (/tag/g, block._tag)
  ();

block.paragraph = replace(block.paragraph)
  ('hr', block.hr)
  ('heading', block.heading)
  ('lheading', block.lheading)
  ('blockquote', block.blockquote)
  ('tag', '<' + block._tag)
  ('def', block.def)
  ();

/**
 * Normal Block Grammar
 */

block.normal = merge({}, block);

/**
 * GFM Block Grammar
 */

block.gfm = merge({}, block.normal, {
  fences: /^ *(`{3,}|~{3,})[ \.]*(\S+)? *\n([\s\S]*?)\s*\1 *(?:\n+|$)/,
  paragraph: /^/,
  heading: /^ *(#{1,6}) +([^\n]+?) *#* *(?:\n+|$)/
});

block.gfm.paragraph = replace(block.paragraph)
  ('(?!', '(?!'
    + block.gfm.fences.source.replace('\\1', '\\2') + '|'
    + block.list.source.replace('\\1', '\\3') + '|')
  ();

/**
 * GFM + Tables Block Grammar
 */

block.tables = merge({}, block.gfm, {
  nptable: /^ *(\S.*\|.*)\n *([-:]+ *\|[-| :]*)\n((?:.*\|.*(?:\n|$))*)\n*/,
  table: /^ *\|(.+)\n *\|( *[-:]+[-| :]*)\n((?: *\|.*(?:\n|$))*)\n*/
});

/**
 * Block Lexer
 */

function Lexer(options) {
  this.tokens = [];
  this.tokens.links = {};
  this.options = options || marked.defaults;
  this.rules = block.normal;

  if (this.options.gfm) {
    if (this.options.tables) {
      this.rules = block.tables;
    } else {
      this.rules = block.gfm;
    }
  }
}

/**
 * Expose Block Rules
 */

Lexer.rules = block;

/**
 * Static Lex Method
 */

Lexer.lex = function(src, options) {
  var lexer = new Lexer(options);
  return lexer.lex(src);
};

/**
 * Preprocessing
 */

Lexer.prototype.lex = function(src) {
  src = src
    .replace(/\r\n|\r/g, '\n')
    .replace(/\t/g, '    ')
    .replace(/\u00a0/g, ' ')
    .replace(/\u2424/g, '\n');

  return this.token(src, true);
};

/**
 * Lexing
 */

Lexer.prototype.token = function(src, top, bq) {
  var src = src.replace(/^ +$/gm, '')
    , next
    , loose
    , cap
    , bull
    , b
    , item
    , space
    , i
    , l;

  while (src) {
    // newline
    if (cap = this.rules.newline.exec(src)) {
      src = src.substring(cap[0].length);
      if (cap[0].length > 1) {
        this.tokens.push({
          type: 'space'
        });
      }
    }

    // code
    if (cap = this.rules.code.exec(src)) {
      src = src.substring(cap[0].length);
      cap = cap[0].replace(/^ {4}/gm, '');
      this.tokens.push({
        type: 'code',
        text: !this.options.pedantic
          ? cap.replace(/\n+$/, '')
          : cap
      });
      continue;
    }

    // fences (gfm)
    if (cap = this.rules.fences.exec(src)) {
      src = src.substring(cap[0].length);
      this.tokens.push({
        type: 'code',
        lang: cap[2],
        text: cap[3] || ''
      });
      continue;
    }

    // heading
    if (cap = this.rules.heading.exec(src)) {
      src = src.substring(cap[0].length);
      this.tokens.push({
        type: 'heading',
        depth: cap[1].length,
        text: cap[2]
      });
      continue;
    }

    // table no leading pipe (gfm)
    if (top && (cap = this.rules.nptable.exec(src))) {
      src = src.substring(cap[0].length);

      item = {
        type: 'table',
        header: cap[1].replace(/^ *| *\| *$/g, '').split(/ *\| */),
        align: cap[2].replace(/^ *|\| *$/g, '').split(/ *\| */),
        cells: cap[3].replace(/\n$/, '').split('\n')
      };

      for (i = 0; i < item.align.length; i++) {
        if (/^ *-+: *$/.test(item.align[i])) {
          item.align[i] = 'right';
        } else if (/^ *:-+: *$/.test(item.align[i])) {
          item.align[i] = 'center';
        } else if (/^ *:-+ *$/.test(item.align[i])) {
          item.align[i] = 'left';
        } else {
          item.align[i] = null;
        }
      }

      for (i = 0; i < item.cells.length; i++) {
        item.cells[i] = item.cells[i].split(/ *\| */);
      }

      this.tokens.push(item);

      continue;
    }

    // lheading
    if (cap = this.rules.lheading.exec(src)) {
      src = src.substring(cap[0].length);
      this.tokens.push({
        type: 'heading',
        depth: cap[2] === '=' ? 1 : 2,
        text: cap[1]
      });
      continue;
    }

    // hr
    if (cap = this.rules.hr.exec(src)) {
      src = src.substring(cap[0].length);
      this.tokens.push({
        type: 'hr'
      });
      continue;
    }

    // blockquote
    if (cap = this.rules.blockquote.exec(src)) {
      src = src.substring(cap[0].length);

      this.tokens.push({
        type: 'blockquote_start'
      });

      cap = cap[0].replace(/^ *> ?/gm, '');

      // Pass `top` to keep the current
      // "toplevel" state. This is exactly
      // how markdown.pl works.
      this.token(cap, top, true);

      this.tokens.push({
        type: 'blockquote_end'
      });

      continue;
    }

    // list
    if (cap = this.rules.list.exec(src)) {
      src = src.substring(cap[0].length);
      bull = cap[2];

      this.tokens.push({
        type: 'list_start',
        ordered: bull.length > 1
      });

      // Get each top-level item.
      cap = cap[0].match(this.rules.item);

      next = false;
      l = cap.length;
      i = 0;

      for (; i < l; i++) {
        item = cap[i];

        // Remove the list item's bullet
        // so it is seen as the next token.
        space = item.length;
        item = item.replace(/^ *([*+-]|\d+\.) +/, '');

        // Outdent whatever the
        // list item contains. Hacky.
        if (~item.indexOf('\n ')) {
          space -= item.length;
          item = !this.options.pedantic
            ? item.replace(new RegExp('^ {1,' + space + '}', 'gm'), '')
            : item.replace(/^ {1,4}/gm, '');
        }

        // Determine whether the next list item belongs here.
        // Backpedal if it does not belong in this list.
        if (this.options.smartLists && i !== l - 1) {
          b = block.bullet.exec(cap[i + 1])[0];
          if (bull !== b && !(bull.length > 1 && b.length > 1)) {
            src = cap.slice(i + 1).join('\n') + src;
            i = l - 1;
          }
        }

        // Determine whether item is loose or not.
        // Use: /(^|\n)(?! )[^\n]+\n\n(?!\s*$)/
        // for discount behavior.
        loose = next || /\n\n(?!\s*$)/.test(item);
        if (i !== l - 1) {
          next = item.charAt(item.length - 1) === '\n';
          if (!loose) loose = next;
        }

        this.tokens.push({
          type: loose
            ? 'loose_item_start'
            : 'list_item_start'
        });

        // Recurse.
        this.token(item, false, bq);

        this.tokens.push({
          type: 'list_item_end'
        });
      }

      this.tokens.push({
        type: 'list_end'
      });

      continue;
    }

    // html
    if (cap = this.rules.html.exec(src)) {
      src = src.substring(cap[0].length);
      this.tokens.push({
        type: this.options.sanitize
          ? 'paragraph'
          : 'html',
        pre: !this.options.sanitizer
          && (cap[1] === 'pre' || cap[1] === 'script' || cap[1] === 'style'),
        text: cap[0]
      });
      continue;
    }

    // def
    if ((!bq && top) && (cap = this.rules.def.exec(src))) {
      src = src.substring(cap[0].length);
      this.tokens.links[cap[1].toLowerCase()] = {
        href: cap[2],
        title: cap[3]
      };
      continue;
    }

    // table (gfm)
    if (top && (cap = this.rules.table.exec(src))) {
      src = src.substring(cap[0].length);

      item = {
        type: 'table',
        header: cap[1].replace(/^ *| *\| *$/g, '').split(/ *\| */),
        align: cap[2].replace(/^ *|\| *$/g, '').split(/ *\| */),
        cells: cap[3].replace(/(?: *\| *)?\n$/, '').split('\n')
      };

      for (i = 0; i < item.align.length; i++) {
        if (/^ *-+: *$/.test(item.align[i])) {
          item.align[i] = 'right';
        } else if (/^ *:-+: *$/.test(item.align[i])) {
          item.align[i] = 'center';
        } else if (/^ *:-+ *$/.test(item.align[i])) {
          item.align[i] = 'left';
        } else {
          item.align[i] = null;
        }
      }

      for (i = 0; i < item.cells.length; i++) {
        item.cells[i] = item.cells[i]
          .replace(/^ *\| *| *\| *$/g, '')
          .split(/ *\| */);
      }

      this.tokens.push(item);

      continue;
    }

    // top-level paragraph
    if (top && (cap = this.rules.paragraph.exec(src))) {
      src = src.substring(cap[0].length);
      this.tokens.push({
        type: 'paragraph',
        text: cap[1].charAt(cap[1].length - 1) === '\n'
          ? cap[1].slice(0, -1)
          : cap[1]
      });
      continue;
    }

    // text
    if (cap = this.rules.text.exec(src)) {
      // Top-level should never reach here.
      src = src.substring(cap[0].length);
      this.tokens.push({
        type: 'text',
        text: cap[0]
      });
      continue;
    }

    if (src) {
      throw new
        Error('Infinite loop on byte: ' + src.charCodeAt(0));
    }
  }

  return this.tokens;
};

/**
 * Inline-Level Grammar
 */

var inline = {
  escape: /^\\([\\`*{}\[\]()#+\-.!_>])/,
  autolink: /^<([^ >]+(@|:\/)[^ >]+)>/,
  url: noop,
  tag: /^<!--[\s\S]*?-->|^<\/?\w+(?:"[^"]*"|'[^']*'|[^'">])*?>/,
  link: /^!?\[(inside)\]\(href\)/,
  reflink: /^!?\[(inside)\]\s*\[([^\]]*)\]/,
  nolink: /^!?\[((?:\[[^\]]*\]|[^\[\]])*)\]/,
  strong: /^__([\s\S]+?)__(?!_)|^\*\*([\s\S]+?)\*\*(?!\*)/,
  em: /^\b_((?:[^_]|__)+?)_\b|^\*((?:\*\*|[\s\S])+?)\*(?!\*)/,
  code: /^(`+)\s*([\s\S]*?[^`])\s*\1(?!`)/,
  br: /^ {2,}\n(?!\s*$)/,
  del: noop,
  text: /^[\s\S]+?(?=[\\<!\[_*`]| {2,}\n|$)/
};

inline._inside = /(?:\[[^\]]*\]|[^\[\]]|\](?=[^\[]*\]))*/;
inline._href = /\s*<?([\s\S]*?)>?(?:\s+['"]([\s\S]*?)['"])?\s*/;

inline.link = replace(inline.link)
  ('inside', inline._inside)
  ('href', inline._href)
  ();

inline.reflink = replace(inline.reflink)
  ('inside', inline._inside)
  ();

/**
 * Normal Inline Grammar
 */

inline.normal = merge({}, inline);

/**
 * Pedantic Inline Grammar
 */

inline.pedantic = merge({}, inline.normal, {
  strong: /^__(?=\S)([\s\S]*?\S)__(?!_)|^\*\*(?=\S)([\s\S]*?\S)\*\*(?!\*)/,
  em: /^_(?=\S)([\s\S]*?\S)_(?!_)|^\*(?=\S)([\s\S]*?\S)\*(?!\*)/
});

/**
 * GFM Inline Grammar
 */

inline.gfm = merge({}, inline.normal, {
  escape: replace(inline.escape)('])', '~|])')(),
  url: /^(https?:\/\/[^\s<]+[^<.,:;"')\]\s])/,
  del: /^~~(?=\S)([\s\S]*?\S)~~/,
  text: replace(inline.text)
    (']|', '~]|')
    ('|', '|https?://|')
    ()
});

/**
 * GFM + Line Breaks Inline Grammar
 */

inline.breaks = merge({}, inline.gfm, {
  br: replace(inline.br)('{2,}', '*')(),
  text: replace(inline.gfm.text)('{2,}', '*')()
});

/**
 * Inline Lexer & Compiler
 */

function InlineLexer(links, options) {
  this.options = options || marked.defaults;
  this.links = links;
  this.rules = inline.normal;
  this.renderer = this.options.renderer || new Renderer;
  this.renderer.options = this.options;

  if (!this.links) {
    throw new
      Error('Tokens array requires a `links` property.');
  }

  if (this.options.gfm) {
    if (this.options.breaks) {
      this.rules = inline.breaks;
    } else {
      this.rules = inline.gfm;
    }
  } else if (this.options.pedantic) {
    this.rules = inline.pedantic;
  }
}

/**
 * Expose Inline Rules
 */

InlineLexer.rules = inline;

/**
 * Static Lexing/Compiling Method
 */

InlineLexer.output = function(src, links, options) {
  var inline = new InlineLexer(links, options);
  return inline.output(src);
};

/**
 * Lexing/Compiling
 */

InlineLexer.prototype.output = function(src) {
  var out = ''
    , link
    , text
    , href
    , cap;

  while (src) {
    // escape
    if (cap = this.rules.escape.exec(src)) {
      src = src.substring(cap[0].length);
      out += cap[1];
      continue;
    }

    // autolink
    if (cap = this.rules.autolink.exec(src)) {
      src = src.substring(cap[0].length);
      if (cap[2] === '@') {
        text = cap[1].charAt(6) === ':'
          ? this.mangle(cap[1].substring(7))
          : this.mangle(cap[1]);
        href = this.mangle('mailto:') + text;
      } else {
        text = escape(cap[1]);
        href = text;
      }
      out += this.renderer.link(href, null, text);
      continue;
    }

    // url (gfm)
    if (!this.inLink && (cap = this.rules.url.exec(src))) {
      src = src.substring(cap[0].length);
      text = escape(cap[1]);
      href = text;
      out += this.renderer.link(href, null, text);
      continue;
    }

    // tag
    if (cap = this.rules.tag.exec(src)) {
      if (!this.inLink && /^<a /i.test(cap[0])) {
        this.inLink = true;
      } else if (this.inLink && /^<\/a>/i.test(cap[0])) {
        this.inLink = false;
      }
      src = src.substring(cap[0].length);
      out += this.options.sanitize
        ? this.options.sanitizer
          ? this.options.sanitizer(cap[0])
          : escape(cap[0])
        : cap[0]
      continue;
    }

    // link
    if (cap = this.rules.link.exec(src)) {
      src = src.substring(cap[0].length);
      this.inLink = true;
      out += this.outputLink(cap, {
        href: cap[2],
        title: cap[3]
      });
      this.inLink = false;
      continue;
    }

    // reflink, nolink
    if ((cap = this.rules.reflink.exec(src))
        || (cap = this.rules.nolink.exec(src))) {
      src = src.substring(cap[0].length);
      link = (cap[2] || cap[1]).replace(/\s+/g, ' ');
      link = this.links[link.toLowerCase()];
      if (!link || !link.href) {
        out += cap[0].charAt(0);
        src = cap[0].substring(1) + src;
        continue;
      }
      this.inLink = true;
      out += this.outputLink(cap, link);
      this.inLink = false;
      continue;
    }

    // strong
    if (cap = this.rules.strong.exec(src)) {
      src = src.substring(cap[0].length);
      out += this.renderer.strong(this.output(cap[2] || cap[1]));
      continue;
    }

    // em
    if (cap = this.rules.em.exec(src)) {
      src = src.substring(cap[0].length);
      out += this.renderer.em(this.output(cap[2] || cap[1]));
      continue;
    }

    // code
    if (cap = this.rules.code.exec(src)) {
      src = src.substring(cap[0].length);
      out += this.renderer.codespan(escape(cap[2], true));
      continue;
    }

    // br
    if (cap = this.rules.br.exec(src)) {
      src = src.substring(cap[0].length);
      out += this.renderer.br();
      continue;
    }

    // del (gfm)
    if (cap = this.rules.del.exec(src)) {
      src = src.substring(cap[0].length);
      out += this.renderer.del(this.output(cap[1]));
      continue;
    }

    // text
    if (cap = this.rules.text.exec(src)) {
      src = src.substring(cap[0].length);
      out += this.renderer.text(escape(this.smartypants(cap[0])));
      continue;
    }

    if (src) {
      throw new
        Error('Infinite loop on byte: ' + src.charCodeAt(0));
    }
  }

  return out;
};

/**
 * Compile Link
 */

InlineLexer.prototype.outputLink = function(cap, link) {
  var href = escape(link.href)
    , title = link.title ? escape(link.title) : null;

  return cap[0].charAt(0) !== '!'
    ? this.renderer.link(href, title, this.output(cap[1]))
    : this.renderer.image(href, title, escape(cap[1]));
};

/**
 * Smartypants Transformations
 */

InlineLexer.prototype.smartypants = function(text) {
  if (!this.options.smartypants) return text;
  return text
    // em-dashes
    .replace(/---/g, '\u2014')
    // en-dashes
    .replace(/--/g, '\u2013')
    // opening singles
    .replace(/(^|[-\u2014/(\[{"\s])'/g, '$1\u2018')
    // closing singles & apostrophes
    .replace(/'/g, '\u2019')
    // opening doubles
    .replace(/(^|[-\u2014/(\[{\u2018\s])"/g, '$1\u201c')
    // closing doubles
    .replace(/"/g, '\u201d')
    // ellipses
    .replace(/\.{3}/g, '\u2026');
};

/**
 * Mangle Links
 */

InlineLexer.prototype.mangle = function(text) {
  if (!this.options.mangle) return text;
  var out = ''
    , l = text.length
    , i = 0
    , ch;

  for (; i < l; i++) {
    ch = text.charCodeAt(i);
    if (Math.random() > 0.5) {
      ch = 'x' + ch.toString(16);
    }
    out += '&#' + ch + ';';
  }

  return out;
};

/**
 * Renderer
 */

function Renderer(options) {
  this.options = options || {};
}

Renderer.prototype.code = function(code, lang, escaped) {
  if (this.options.highlight) {
    var out = this.options.highlight(code, lang);
    if (out != null && out !== code) {
      escaped = true;
      code = out;
    }
  }

  if (!lang) {
    return '<pre><code>'
      + (escaped ? code : escape(code, true))
      + '\n</code></pre>';
  }

  return '<pre><code class="'
    + this.options.langPrefix
    + escape(lang, true)
    + '">'
    + (escaped ? code : escape(code, true))
    + '\n</code></pre>\n';
};

Renderer.prototype.blockquote = function(quote) {
  return '<blockquote>\n' + quote + '</blockquote>\n';
};

Renderer.prototype.html = function(html) {
  return html;
};

Renderer.prototype.heading = function(text, level, raw) {
  return '<h'
    + level
    + ' id="'
    + this.options.headerPrefix
    + raw.toLowerCase().replace(/[^\w]+/g, '-')
    + '">'
    + text
    + '</h'
    + level
    + '>\n';
};

Renderer.prototype.hr = function() {
  return this.options.xhtml ? '<hr/>\n' : '<hr>\n';
};

Renderer.prototype.list = function(body, ordered) {
  var type = ordered ? 'ol' : 'ul';
  return '<' + type + '>\n' + body + '</' + type + '>\n';
};

Renderer.prototype.listitem = function(text) {
  return '<li>' + text + '</li>\n';
};

Renderer.prototype.paragraph = function(text) {
  return '<p>' + text + '</p>\n';
};

Renderer.prototype.table = function(header, body) {
  return '<table>\n'
    + '<thead>\n'
    + header
    + '</thead>\n'
    + '<tbody>\n'
    + body
    + '</tbody>\n'
    + '</table>\n';
};

Renderer.prototype.tablerow = function(content) {
  return '<tr>\n' + content + '</tr>\n';
};

Renderer.prototype.tablecell = function(content, flags) {
  var type = flags.header ? 'th' : 'td';
  var tag = flags.align
    ? '<' + type + ' style="text-align:' + flags.align + '">'
    : '<' + type + '>';
  return tag + content + '</' + type + '>\n';
};

// span level renderer
Renderer.prototype.strong = function(text) {
  return '<strong>' + text + '</strong>';
};

Renderer.prototype.em = function(text) {
  return '<em>' + text + '</em>';
};

Renderer.prototype.codespan = function(text) {
  return '<code>' + text + '</code>';
};

Renderer.prototype.br = function() {
  return this.options.xhtml ? '<br/>' : '<br>';
};

Renderer.prototype.del = function(text) {
  return '<del>' + text + '</del>';
};

Renderer.prototype.link = function(href, title, text) {
  if (this.options.sanitize) {
    try {
      var prot = decodeURIComponent(unescape(href))
        .replace(/[^\w:]/g, '')
        .toLowerCase();
    } catch (e) {
      return '';
    }
    if (prot.indexOf('javascript:') === 0 || prot.indexOf('vbscript:') === 0) {
      return '';
    }
  }
  var out = '<a href="' + href + '"';
  if (title) {
    out += ' title="' + title + '"';
  }
  out += '>' + text + '</a>';
  return out;
};

Renderer.prototype.image = function(href, title, text) {
  var out = '<img src="' + href + '" alt="' + text + '"';
  if (title) {
    out += ' title="' + title + '"';
  }
  out += this.options.xhtml ? '/>' : '>';
  return out;
};

Renderer.prototype.text = function(text) {
  return text;
};

/**
 * Parsing & Compiling
 */

function Parser(options) {
  this.tokens = [];
  this.token = null;
  this.options = options || marked.defaults;
  this.options.renderer = this.options.renderer || new Renderer;
  this.renderer = this.options.renderer;
  this.renderer.options = this.options;
}

/**
 * Static Parse Method
 */

Parser.parse = function(src, options, renderer) {
  var parser = new Parser(options, renderer);
  return parser.parse(src);
};

/**
 * Parse Loop
 */

Parser.prototype.parse = function(src) {
  this.inline = new InlineLexer(src.links, this.options, this.renderer);
  this.tokens = src.reverse();

  var out = '';
  while (this.next()) {
    out += this.tok();
  }

  return out;
};

/**
 * Next Token
 */

Parser.prototype.next = function() {
  return this.token = this.tokens.pop();
};

/**
 * Preview Next Token
 */

Parser.prototype.peek = function() {
  return this.tokens[this.tokens.length - 1] || 0;
};

/**
 * Parse Text Tokens
 */

Parser.prototype.parseText = function() {
  var body = this.token.text;

  while (this.peek().type === 'text') {
    body += '\n' + this.next().text;
  }

  return this.inline.output(body);
};

/**
 * Parse Current Token
 */

Parser.prototype.tok = function() {
  switch (this.token.type) {
    case 'space': {
      return '';
    }
    case 'hr': {
      return this.renderer.hr();
    }
    case 'heading': {
      return this.renderer.heading(
        this.inline.output(this.token.text),
        this.token.depth,
        this.token.text);
    }
    case 'code': {
      return this.renderer.code(this.token.text,
        this.token.lang,
        this.token.escaped);
    }
    case 'table': {
      var header = ''
        , body = ''
        , i
        , row
        , cell
        , flags
        , j;

      // header
      cell = '';
      for (i = 0; i < this.token.header.length; i++) {
        flags = { header: true, align: this.token.align[i] };
        cell += this.renderer.tablecell(
          this.inline.output(this.token.header[i]),
          { header: true, align: this.token.align[i] }
        );
      }
      header += this.renderer.tablerow(cell);

      for (i = 0; i < this.token.cells.length; i++) {
        row = this.token.cells[i];

        cell = '';
        for (j = 0; j < row.length; j++) {
          cell += this.renderer.tablecell(
            this.inline.output(row[j]),
            { header: false, align: this.token.align[j] }
          );
        }

        body += this.renderer.tablerow(cell);
      }
      return this.renderer.table(header, body);
    }
    case 'blockquote_start': {
      var body = '';

      while (this.next().type !== 'blockquote_end') {
        body += this.tok();
      }

      return this.renderer.blockquote(body);
    }
    case 'list_start': {
      var body = ''
        , ordered = this.token.ordered;

      while (this.next().type !== 'list_end') {
        body += this.tok();
      }

      return this.renderer.list(body, ordered);
    }
    case 'list_item_start': {
      var body = '';

      while (this.next().type !== 'list_item_end') {
        body += this.token.type === 'text'
          ? this.parseText()
          : this.tok();
      }

      return this.renderer.listitem(body);
    }
    case 'loose_item_start': {
      var body = '';

      while (this.next().type !== 'list_item_end') {
        body += this.tok();
      }

      return this.renderer.listitem(body);
    }
    case 'html': {
      var html = !this.token.pre && !this.options.pedantic
        ? this.inline.output(this.token.text)
        : this.token.text;
      return this.renderer.html(html);
    }
    case 'paragraph': {
      return this.renderer.paragraph(this.inline.output(this.token.text));
    }
    case 'text': {
      return this.renderer.paragraph(this.parseText());
    }
  }
};

/**
 * Helpers
 */

function escape(html, encode) {
  return html
    .replace(!encode ? /&(?!#?\w+;)/g : /&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function unescape(html) {
	// explicitly match decimal, hex, and named HTML entities 
  return html.replace(/&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/g, function(_, n) {
    n = n.toLowerCase();
    if (n === 'colon') return ':';
    if (n.charAt(0) === '#') {
      return n.charAt(1) === 'x'
        ? String.fromCharCode(parseInt(n.substring(2), 16))
        : String.fromCharCode(+n.substring(1));
    }
    return '';
  });
}

function replace(regex, opt) {
  regex = regex.source;
  opt = opt || '';
  return function self(name, val) {
    if (!name) return new RegExp(regex, opt);
    val = val.source || val;
    val = val.replace(/(^|[^\[])\^/g, '$1');
    regex = regex.replace(name, val);
    return self;
  };
}

function noop() {}
noop.exec = noop;

function merge(obj) {
  var i = 1
    , target
    , key;

  for (; i < arguments.length; i++) {
    target = arguments[i];
    for (key in target) {
      if (Object.prototype.hasOwnProperty.call(target, key)) {
        obj[key] = target[key];
      }
    }
  }

  return obj;
}


/**
 * Marked
 */

function marked(src, opt, callback) {
  if (callback || typeof opt === 'function') {
    if (!callback) {
      callback = opt;
      opt = null;
    }

    opt = merge({}, marked.defaults, opt || {});

    var highlight = opt.highlight
      , tokens
      , pending
      , i = 0;

    try {
      tokens = Lexer.lex(src, opt)
    } catch (e) {
      return callback(e);
    }

    pending = tokens.length;

    var done = function(err) {
      if (err) {
        opt.highlight = highlight;
        return callback(err);
      }

      var out;

      try {
        out = Parser.parse(tokens, opt);
      } catch (e) {
        err = e;
      }

      opt.highlight = highlight;

      return err
        ? callback(err)
        : callback(null, out);
    };

    if (!highlight || highlight.length < 3) {
      return done();
    }

    delete opt.highlight;

    if (!pending) return done();

    for (; i < tokens.length; i++) {
      (function(token) {
        if (token.type !== 'code') {
          return --pending || done();
        }
        return highlight(token.text, token.lang, function(err, code) {
          if (err) return done(err);
          if (code == null || code === token.text) {
            return --pending || done();
          }
          token.text = code;
          token.escaped = true;
          --pending || done();
        });
      })(tokens[i]);
    }

    return;
  }
  try {
    if (opt) opt = merge({}, marked.defaults, opt);
    return Parser.parse(Lexer.lex(src, opt), opt);
  } catch (e) {
    e.message += '\nPlease report this to https://github.com/chjj/marked.';
    if ((opt || marked.defaults).silent) {
      return '<p>An error occured:</p><pre>'
        + escape(e.message + '', true)
        + '</pre>';
    }
    throw e;
  }
}

/**
 * Options
 */

marked.options =
marked.setOptions = function(opt) {
  merge(marked.defaults, opt);
  return marked;
};

marked.defaults = {
  gfm: true,
  tables: true,
  breaks: false,
  pedantic: false,
  sanitize: false,
  sanitizer: null,
  mangle: true,
  smartLists: false,
  silent: false,
  highlight: null,
  langPrefix: 'lang-',
  smartypants: false,
  headerPrefix: '',
  renderer: new Renderer,
  xhtml: false
};

/**
 * Expose
 */

marked.Parser = Parser;
marked.parser = Parser.parse;

marked.Renderer = Renderer;

marked.Lexer = Lexer;
marked.lexer = Lexer.lex;

marked.InlineLexer = InlineLexer;
marked.inlineLexer = InlineLexer.output;

marked.parse = marked;

if (true) {
  module.exports = marked;
} else if (typeof define === 'function' && define.amd) {
  define(function() { return marked; });
} else {
  this.marked = marked;
}

}).call(function() {
  return this || (typeof window !== 'undefined' ? window : global);
}());

/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(/*! ./../../webpack/buildin/global.js */ 7)))

/***/ }),
/* 43 */
/* no static exports found */
/* all exports used */
/*!***********************!*\
  !*** ./src/spec.json ***!
  \***********************/
/***/ (function(module, exports) {

module.exports = {
	"version": "1.0.0",
	"errors": {
		"io-error": {
			"name": "IO Error",
			"type": "source",
			"context": "table",
			"weight": 100,
			"message": "The data source returned an IO Error of type {error_type}",
			"description": "Data reading error because of IO error.\n\n How it could be resolved:\n - Fix path if it's not correct."
		},
		"http-error": {
			"name": "HTTP Error",
			"type": "source",
			"context": "table",
			"weight": 100,
			"message": "The data source returned an HTTP error with a status code of {status_code}",
			"description": "Data reading error because of HTTP error.\n\n How it could be resolved:\n - Fix url link if it's not correct."
		},
		"source-error": {
			"name": "Source Error",
			"type": "source",
			"context": "table",
			"weight": 100,
			"message": "The data source has not supported or has inconsistent contents; no tabular data can be extracted",
			"description": "Data reading error because of not supported or inconsistent contents.\n\n How it could be resolved:\n - Fix data contents (e.g. change JSON data to array or arrays/objects).\n - Set correct source settings in {validator}."
		},
		"scheme-error": {
			"name": "Scheme Error",
			"type": "source",
			"context": "table",
			"weight": 100,
			"message": "The data source is in an unknown scheme; no tabular data can be extracted",
			"description": "Data reading error because of incorrect scheme.\n\n How it could be resolved:\n - Fix data scheme (e.g. change scheme from `ftp` to `http`).\n - Set correct scheme in {validator}."
		},
		"format-error": {
			"name": "Format Error",
			"type": "source",
			"context": "table",
			"weight": 100,
			"message": "The data source is in an unknown format; no tabular data can be extracted",
			"description": "Data reading error because of incorrect format.\n\n How it could be resolved:\n - Fix data format (e.g. change file extension from `txt` to `csv`).\n - Set correct format in {validator}."
		},
		"encoding-error": {
			"name": "Encoding Error",
			"type": "source",
			"context": "table",
			"weight": 100,
			"message": "The data source could not be successfully decoded with {encoding} encoding",
			"description": "Data reading error because of an encoding problem.\n\n How it could be resolved:\n - Fix data source if it's broken.\n - Set correct encoding in {validator}."
		},
		"blank-header": {
			"name": "Blank Header",
			"type": "structure",
			"context": "head",
			"weight": 3,
			"message": "Header in column {column_number} is blank",
			"description": "A column in the header row is missing a value. Column names should be provided.\n\n How it could be resolved:\n - Add the missing column name to the first row of the data source.\n - If the first row starts with, or ends with a comma, remove it.\n - If this error should be ignored disable `blank-header` check in {validator}."
		},
		"duplicate-header": {
			"name": "Duplicate Header",
			"type": "structure",
			"context": "head",
			"weight": 3,
			"message": "Header in column {column_number} is duplicated to header in column(s) {column_numbers}",
			"description": "Two columns in the header row have the same value. Column names should be unique.\n\n How it could be resolved:\n - Add the missing column name to the first row of the data.\n - If the first row starts with, or ends with a comma, remove it.\n - If this error should be ignored disable `duplicate-header` check in {validator}."
		},
		"blank-row": {
			"name": "Blank Row",
			"type": "structure",
			"context": "body",
			"weight": 9,
			"message": "Row {row_number} is completely blank",
			"description": "This row is empty. A row should contain at least one value.\n\n How it could be resolved:\n - Delete the row.\n - If this error should be ignored disable `blank-row` check in {validator}."
		},
		"duplicate-row": {
			"name": "Duplicate Row",
			"type": "structure",
			"context": "body",
			"weight": 5,
			"message": "Row {row_number} is duplicated to row(s) {row_numbers}",
			"description": "The exact same data has been seen in another row.\n\n How it could be resolved:\n - If some of the data is incorrect, correct it.\n - If the whole row is an incorrect duplicate, remove it.\n - If this error should be ignored disable `duplicate-row` check in {validator}."
		},
		"extra-value": {
			"name": "Extra Value",
			"type": "structure",
			"context": "body",
			"weight": 9,
			"message": "Row {row_number} has an extra value in column {column_number}",
			"description": "This row has more values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.\n\n How it could be resolved:\n - Check data has an extra comma between the values in this row.\n - If this error should be ignored disable `extra-value` check in {validator}."
		},
		"missing-value": {
			"name": "Missing Value",
			"type": "structure",
			"context": "body",
			"weight": 9,
			"message": "Row {row_number} has a missing value in column {column_number}",
			"description": "This row has less values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.\n\n How it could be resolved:\n - Check data is not missing a comma between the values in this row.\n - If this error should be ignored disable `missing-value` check in {validator}."
		},
		"schema-error": {
			"name": "Table Schema Error",
			"type": "schema",
			"context": "table",
			"weight": 15,
			"message": "Table Schema error: {error_message}",
			"description": "Provided schema is not valid.\n\n How it could be resolved:\n - Update schema descriptor to be a valid descriptor\n - If this error should be ignored disable schema cheks in {validator}."
		},
		"non-matching-header": {
			"name": "Non-Matching Header",
			"type": "schema",
			"context": "head",
			"weight": 9,
			"message": "Header in column {column_number} doesn't match field name {field_name} in the schema",
			"description": "One of the data source headers doesn't match the field name defined in the schema.\n\n How it could be resolved:\n - Rename header in the data source or field in the schema\n - If this error should be ignored disable `non-matching-header` check in {validator}."
		},
		"extra-header": {
			"name": "Extra Header",
			"type": "schema",
			"context": "head",
			"weight": 9,
			"message": "There is an extra header in column {column_number}",
			"description": "The first row of the data source contains header that doesn't exist in the schema.\n\n How it could be resolved:\n - Remove the extra column from the data source or add the missing field to the schema\n - If this error should be ignored disable `extra-header` check in {validator}."
		},
		"missing-header": {
			"name": "Missing Header",
			"type": "schema",
			"context": "head",
			"weight": 9,
			"message": "There is a missing header in column {column_number}",
			"description": "Based on the schema there should be a header that is missing in the first row of the data source.\n\n How it could be resolved:\n - Add the missing column to the data source or remove the extra field from the schema\n - If this error should be ignored disable `missing-header` check in {validator}."
		},
		"type-or-format-error": {
			"name": "Type or Format Error",
			"type": "schema",
			"context": "body",
			"weight": 9,
			"message": "The value {value} in row {row_number} and column {column_number} is not type {field_type} and format {field_format}",
			"description": "The value does not match the schema type and format for this field.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If this value is correct, adjust the type and/or format.\n - To ignore the error, disable the `type-or-format-error` check in {validator}. In this case all schema checks for row values will be ignored."
		},
		"required-constraint": {
			"name": "Required Constraint",
			"type": "schema",
			"context": "body",
			"weight": 9,
			"message": "Column {column_number} is a required field, but row {row_number} has no value",
			"description": "This field is a required field, but it contains no value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove the `required` constraint from the schema.\n - If this error should be ignored disable `required-constraint` check in {validator}."
		},
		"pattern-constraint": {
			"name": "Pattern Constraint",
			"type": "schema",
			"context": "body",
			"weight": 7,
			"message": "The value {value} in row {row_number} and column {column_number} does not conform to the pattern constraint of {constraint}",
			"description": "This field value should conform to constraint pattern.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `pattern` constraint in the schema.\n - If this error should be ignored disable `pattern-constraint` check in {validator}."
		},
		"unique-constraint": {
			"name": "Unique Constraint",
			"type": "schema",
			"context": "body",
			"weight": 9,
			"message": "Rows {row_numbers} has unique constraint violation in column {column_number}",
			"description": "This field is a unique field but it contains a value that has been used in another row.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then the values in this column are not unique. Remove the `unique` constraint from the schema.\n - If this error should be ignored disable `unique-constraint` check in {validator}."
		},
		"enumerable-constraint": {
			"name": "Enumerable Constraint",
			"type": "schema",
			"context": "body",
			"weight": 7,
			"message": "The value {value} in row {row_number} and column {column_number} does not conform to the given enumeration: {constraint}",
			"description": "This field value should be equal to one of the values in the enumeration constraint.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `enum` constraint in the schema.\n - If this error should be ignored disable `enumerable-constraint` check in {validator}."
		},
		"minimum-constraint": {
			"name": "Minimum Constraint",
			"type": "schema",
			"context": "body",
			"weight": 7,
			"message": "The value {value} in row {row_number} and column {column_number} does not conform to the minimum constraint of {constraint}",
			"description": "This field value should be greater or equal than constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `minimum` constraint in the schema.\n - If this error should be ignored disable `minimum-constraint` check in {validator}."
		},
		"maximum-constraint": {
			"name": "Maximum Constraint",
			"type": "schema",
			"context": "body",
			"weight": 7,
			"message": "The value {value} in row {row_number} and column {column_number} does not conform to the maximum constraint of {constraint}",
			"description": "This field value should be less or equal than constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `maximum` constraint in the schema.\n - If this error should be ignored disable `maximum-constraint` check in {validator}."
		},
		"minimum-length-constraint": {
			"name": "Minimum Length Constraint",
			"type": "schema",
			"context": "body",
			"weight": 7,
			"message": "The value {value} in row {row_number} and column {column_number} does not conform to the minimum length constraint of {constraint}",
			"description": "A lenght of this field value should be greater or equal than schema constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `minimumLength` constraint in the schema.\n - If this error should be ignored disable `minimum-length-constraint` check in {validator}."
		},
		"maximum-length-constraint": {
			"name": "Maximum Length Constraint",
			"type": "schema",
			"context": "body",
			"weight": 7,
			"message": "The value {value} in row {row_number} and column {column_number} does not conform to the maximum length constraint of {constraint}",
			"description": "A lenght of this field value should be less or equal than schema constraint value.\n\n How it could be resolved:\n - If this value is not correct, update the value.\n - If value is correct, then remove or refine the `maximumLength` constraint in the schema.\n - If this error should be ignored disable `maximum-length-constraint` check in {validator}."
		}
	}
};

/***/ })
/******/ ]);
});