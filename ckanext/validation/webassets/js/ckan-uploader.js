(function(k,j){typeof exports=="object"&&typeof module<"u"?module.exports=j():typeof define=="function"&&define.amd?define(j):(k=typeof globalThis<"u"?globalThis:k||self,k.CkanUploader=j())})(this,function(){"use strict";function k(){}function j(e){return e()}function Ue(){return Object.create(null)}function H(e){e.forEach(j)}function Be(e){return typeof e=="function"}function Le(e,t){return e!=e?t==t:e!==t||e&&typeof e=="object"||typeof e=="function"}function At(e){return Object.keys(e).length===0}function E(e,t){e.appendChild(t)}function A(e,t,n){e.insertBefore(t,n||null)}function S(e){e.parentNode&&e.parentNode.removeChild(e)}function O(e){return document.createElement(e)}function B(e){return document.createTextNode(e)}function F(){return B(" ")}function pe(){return B("")}function M(e,t,n,r){return e.addEventListener(t,n,r),()=>e.removeEventListener(t,n,r)}function y(e,t,n){n==null?e.removeAttribute(t):e.getAttribute(t)!==n&&e.setAttribute(t,n)}function Tt(e){return Array.from(e.childNodes)}function Nt(e,t){t=""+t,e.wholeText!==t&&(e.data=t)}function Y(e,t){e.value=t==null?"":t}function xe(e,t,n,r){n===null?e.style.removeProperty(t):e.style.setProperty(t,n,r?"important":"")}function Z(e,t,n){e.classList[n?"add":"remove"](t)}function kt(e,t,{bubbles:n=!1,cancelable:r=!1}={}){const s=document.createEvent("CustomEvent");return s.initCustomEvent(e,n,r,t),s}let J;function q(e){J=e}function Ct(){if(!J)throw new Error("Function called outside component initialization");return J}function je(){const e=Ct();return(t,n,{cancelable:r=!1}={})=>{const s=e.$$.callbacks[t];if(s){const o=kt(t,n,{cancelable:r});return s.slice().forEach(i=>{i.call(e,o)}),!o.defaultPrevented}return!0}}const V=[],he=[],$=[],He=[],Pt=Promise.resolve();let me=!1;function Ft(){me||(me=!0,Pt.then(Me))}function _e(e){$.push(e)}const ye=new Set;let ee=0;function Me(){const e=J;do{for(;ee<V.length;){const t=V[ee];ee++,q(t),Dt(t.$$)}for(q(null),V.length=0,ee=0;he.length;)he.pop()();for(let t=0;t<$.length;t+=1){const n=$[t];ye.has(n)||(ye.add(n),n())}$.length=0}while(V.length);for(;He.length;)He.pop()();me=!1,ye.clear(),q(e)}function Dt(e){if(e.fragment!==null){e.update(),H(e.before_update);const t=e.dirty;e.dirty=[-1],e.fragment&&e.fragment.p(e.ctx,t),e.after_update.forEach(_e)}}const te=new Set;let Ut;function ve(e,t){e&&e.i&&(te.delete(e),e.i(t))}function Bt(e,t,n,r){if(e&&e.o){if(te.has(e))return;te.add(e),Ut.c.push(()=>{te.delete(e),r&&(n&&e.d(1),r())}),e.o(t)}else r&&r()}function Lt(e){e&&e.c()}function Ie(e,t,n,r){const{fragment:s,after_update:o}=e.$$;s&&s.m(t,n),r||_e(()=>{const i=e.$$.on_mount.map(j).filter(Be);e.$$.on_destroy?e.$$.on_destroy.push(...i):H(i),e.$$.on_mount=[]}),o.forEach(_e)}function ze(e,t){const n=e.$$;n.fragment!==null&&(H(n.on_destroy),n.fragment&&n.fragment.d(t),n.on_destroy=n.fragment=null,n.ctx=[])}function xt(e,t){e.$$.dirty[0]===-1&&(V.push(e),Ft(),e.$$.dirty.fill(0)),e.$$.dirty[t/31|0]|=1<<t%31}function Je(e,t,n,r,s,o,i,u=[-1]){const d=J;q(e);const a=e.$$={fragment:null,ctx:[],props:o,update:k,not_equal:s,bound:Ue(),on_mount:[],on_destroy:[],on_disconnect:[],before_update:[],after_update:[],context:new Map(t.context||(d?d.$$.context:[])),callbacks:Ue(),dirty:u,skip_bound:!1,root:t.target||d.$$.root};i&&i(a.root);let c=!1;if(a.ctx=n?n(e,t.props||{},(f,p,...m)=>{const h=m.length?m[0]:p;return a.ctx&&s(a.ctx[f],a.ctx[f]=h)&&(!a.skip_bound&&a.bound[f]&&a.bound[f](h),c&&xt(e,f)),p}):[],a.update(),c=!0,H(a.before_update),a.fragment=r?r(a.ctx):!1,t.target){if(t.hydrate){const f=Tt(t.target);a.fragment&&a.fragment.l(f),f.forEach(S)}else a.fragment&&a.fragment.c();t.intro&&ve(e.$$.fragment),Ie(e,t.target,t.anchor,t.customElement),Me()}q(d)}class qe{$destroy(){ze(this,1),this.$destroy=k}$on(t,n){if(!Be(n))return k;const r=this.$$.callbacks[t]||(this.$$.callbacks[t]=[]);return r.push(n),()=>{const s=r.indexOf(n);s!==-1&&r.splice(s,1)}}$set(t){this.$$set&&!At(t)&&(this.$$.skip_bound=!0,this.$$set(t),this.$$.skip_bound=!1)}}function Ve(e,t){return function(){return e.apply(t,arguments)}}const{toString:We}=Object.prototype,{getPrototypeOf:be}=Object,Ee=(e=>t=>{const n=We.call(t);return e[n]||(e[n]=n.slice(8,-1).toLowerCase())})(Object.create(null)),D=e=>(e=e.toLowerCase(),t=>Ee(t)===e),ne=e=>t=>typeof t===e,{isArray:v}=Array,W=ne("undefined");function jt(e){return e!==null&&!W(e)&&e.constructor!==null&&!W(e.constructor)&&x(e.constructor.isBuffer)&&e.constructor.isBuffer(e)}const Ke=D("ArrayBuffer");function Ht(e){let t;return typeof ArrayBuffer<"u"&&ArrayBuffer.isView?t=ArrayBuffer.isView(e):t=e&&e.buffer&&Ke(e.buffer),t}const Mt=ne("string"),x=ne("function"),Xe=ne("number"),we=e=>e!==null&&typeof e=="object",vt=e=>e===!0||e===!1,re=e=>{if(Ee(e)!=="object")return!1;const t=be(e);return(t===null||t===Object.prototype||Object.getPrototypeOf(t)===null)&&!(Symbol.toStringTag in e)&&!(Symbol.iterator in e)},It=D("Date"),zt=D("File"),Jt=D("Blob"),qt=D("FileList"),Vt=e=>we(e)&&x(e.pipe),Wt=e=>{const t="[object FormData]";return e&&(typeof FormData=="function"&&e instanceof FormData||We.call(e)===t||x(e.toString)&&e.toString()===t)},Kt=D("URLSearchParams"),Xt=e=>e.trim?e.trim():e.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g,"");function K(e,t,{allOwnKeys:n=!1}={}){if(e===null||typeof e>"u")return;let r,s;if(typeof e!="object"&&(e=[e]),v(e))for(r=0,s=e.length;r<s;r++)t.call(null,e[r],r,e);else{const o=n?Object.getOwnPropertyNames(e):Object.keys(e),i=o.length;let u;for(r=0;r<i;r++)u=o[r],t.call(null,e[u],u,e)}}function Ge(e,t){t=t.toLowerCase();const n=Object.keys(e);let r=n.length,s;for(;r-- >0;)if(s=n[r],t===s.toLowerCase())return s;return null}const Qe=typeof self>"u"?typeof global>"u"?globalThis:global:self,Ye=e=>!W(e)&&e!==Qe;function Oe(){const{caseless:e}=Ye(this)&&this||{},t={},n=(r,s)=>{const o=e&&Ge(t,s)||s;re(t[o])&&re(r)?t[o]=Oe(t[o],r):re(r)?t[o]=Oe({},r):v(r)?t[o]=r.slice():t[o]=r};for(let r=0,s=arguments.length;r<s;r++)arguments[r]&&K(arguments[r],n);return t}const Gt=(e,t,n,{allOwnKeys:r}={})=>(K(t,(s,o)=>{n&&x(s)?e[o]=Ve(s,n):e[o]=s},{allOwnKeys:r}),e),Qt=e=>(e.charCodeAt(0)===65279&&(e=e.slice(1)),e),Yt=(e,t,n,r)=>{e.prototype=Object.create(t.prototype,r),e.prototype.constructor=e,Object.defineProperty(e,"super",{value:t.prototype}),n&&Object.assign(e.prototype,n)},Zt=(e,t,n,r)=>{let s,o,i;const u={};if(t=t||{},e==null)return t;do{for(s=Object.getOwnPropertyNames(e),o=s.length;o-- >0;)i=s[o],(!r||r(i,e,t))&&!u[i]&&(t[i]=e[i],u[i]=!0);e=n!==!1&&be(e)}while(e&&(!n||n(e,t))&&e!==Object.prototype);return t},$t=(e,t,n)=>{e=String(e),(n===void 0||n>e.length)&&(n=e.length),n-=t.length;const r=e.indexOf(t,n);return r!==-1&&r===n},en=e=>{if(!e)return null;if(v(e))return e;let t=e.length;if(!Xe(t))return null;const n=new Array(t);for(;t-- >0;)n[t]=e[t];return n},tn=(e=>t=>e&&t instanceof e)(typeof Uint8Array<"u"&&be(Uint8Array)),nn=(e,t)=>{const r=(e&&e[Symbol.iterator]).call(e);let s;for(;(s=r.next())&&!s.done;){const o=s.value;t.call(e,o[0],o[1])}},rn=(e,t)=>{let n;const r=[];for(;(n=e.exec(t))!==null;)r.push(n);return r},sn=D("HTMLFormElement"),on=e=>e.toLowerCase().replace(/[_-\s]([a-z\d])(\w*)/g,function(n,r,s){return r.toUpperCase()+s}),Ze=(({hasOwnProperty:e})=>(t,n)=>e.call(t,n))(Object.prototype),an=D("RegExp"),$e=(e,t)=>{const n=Object.getOwnPropertyDescriptors(e),r={};K(n,(s,o)=>{t(s,o,e)!==!1&&(r[o]=s)}),Object.defineProperties(e,r)},l={isArray:v,isArrayBuffer:Ke,isBuffer:jt,isFormData:Wt,isArrayBufferView:Ht,isString:Mt,isNumber:Xe,isBoolean:vt,isObject:we,isPlainObject:re,isUndefined:W,isDate:It,isFile:zt,isBlob:Jt,isRegExp:an,isFunction:x,isStream:Vt,isURLSearchParams:Kt,isTypedArray:tn,isFileList:qt,forEach:K,merge:Oe,extend:Gt,trim:Xt,stripBOM:Qt,inherits:Yt,toFlatObject:Zt,kindOf:Ee,kindOfTest:D,endsWith:$t,toArray:en,forEachEntry:nn,matchAll:rn,isHTMLForm:sn,hasOwnProperty:Ze,hasOwnProp:Ze,reduceDescriptors:$e,freezeMethods:e=>{$e(e,(t,n)=>{if(x(e)&&["arguments","caller","callee"].indexOf(n)!==-1)return!1;const r=e[n];if(!!x(r)){if(t.enumerable=!1,"writable"in t){t.writable=!1;return}t.set||(t.set=()=>{throw Error("Can not rewrite read-only method '"+n+"'")})}})},toObjectSet:(e,t)=>{const n={},r=s=>{s.forEach(o=>{n[o]=!0})};return v(e)?r(e):r(String(e).split(t)),n},toCamelCase:on,noop:()=>{},toFiniteNumber:(e,t)=>(e=+e,Number.isFinite(e)?e:t),findKey:Ge,global:Qe,isContextDefined:Ye,toJSONObject:e=>{const t=new Array(10),n=(r,s)=>{if(we(r)){if(t.indexOf(r)>=0)return;if(!("toJSON"in r)){t[s]=r;const o=v(r)?[]:{};return K(r,(i,u)=>{const d=n(i,s+1);!W(d)&&(o[u]=d)}),t[s]=void 0,o}}return r};return n(e,0)}};function b(e,t,n,r,s){Error.call(this),Error.captureStackTrace?Error.captureStackTrace(this,this.constructor):this.stack=new Error().stack,this.message=e,this.name="AxiosError",t&&(this.code=t),n&&(this.config=n),r&&(this.request=r),s&&(this.response=s)}l.inherits(b,Error,{toJSON:function(){return{message:this.message,name:this.name,description:this.description,number:this.number,fileName:this.fileName,lineNumber:this.lineNumber,columnNumber:this.columnNumber,stack:this.stack,config:l.toJSONObject(this.config),code:this.code,status:this.response&&this.response.status?this.response.status:null}}});const et=b.prototype,tt={};["ERR_BAD_OPTION_VALUE","ERR_BAD_OPTION","ECONNABORTED","ETIMEDOUT","ERR_NETWORK","ERR_FR_TOO_MANY_REDIRECTS","ERR_DEPRECATED","ERR_BAD_RESPONSE","ERR_BAD_REQUEST","ERR_CANCELED","ERR_NOT_SUPPORT","ERR_INVALID_URL"].forEach(e=>{tt[e]={value:e}}),Object.defineProperties(b,tt),Object.defineProperty(et,"isAxiosError",{value:!0}),b.from=(e,t,n,r,s,o)=>{const i=Object.create(et);return l.toFlatObject(e,i,function(d){return d!==Error.prototype},u=>u!=="isAxiosError"),b.call(i,e.message,t,n,r,s),i.cause=e,i.name=e.name,o&&Object.assign(i,o),i};var ln=typeof self=="object"?self.FormData:window.FormData;const un=ln;function ge(e){return l.isPlainObject(e)||l.isArray(e)}function nt(e){return l.endsWith(e,"[]")?e.slice(0,-2):e}function rt(e,t,n){return e?e.concat(t).map(function(s,o){return s=nt(s),!n&&o?"["+s+"]":s}).join(n?".":""):t}function cn(e){return l.isArray(e)&&!e.some(ge)}const fn=l.toFlatObject(l,{},null,function(t){return/^is[A-Z]/.test(t)});function dn(e){return e&&l.isFunction(e.append)&&e[Symbol.toStringTag]==="FormData"&&e[Symbol.iterator]}function se(e,t,n){if(!l.isObject(e))throw new TypeError("target must be an object");t=t||new(un||FormData),n=l.toFlatObject(n,{metaTokens:!0,dots:!1,indexes:!1},!1,function(_,T){return!l.isUndefined(T[_])});const r=n.metaTokens,s=n.visitor||c,o=n.dots,i=n.indexes,d=(n.Blob||typeof Blob<"u"&&Blob)&&dn(t);if(!l.isFunction(s))throw new TypeError("visitor must be a function");function a(h){if(h===null)return"";if(l.isDate(h))return h.toISOString();if(!d&&l.isBlob(h))throw new b("Blob is not supported. Use a Buffer instead.");return l.isArrayBuffer(h)||l.isTypedArray(h)?d&&typeof Blob=="function"?new Blob([h]):Buffer.from(h):h}function c(h,_,T){let R=h;if(h&&!T&&typeof h=="object"){if(l.endsWith(_,"{}"))_=r?_:_.slice(0,-2),h=JSON.stringify(h);else if(l.isArray(h)&&cn(h)||l.isFileList(h)||l.endsWith(_,"[]")&&(R=l.toArray(h)))return _=nt(_),R.forEach(function(z,fe){!(l.isUndefined(z)||z===null)&&t.append(i===!0?rt([_],fe,o):i===null?_:_+"[]",a(z))}),!1}return ge(h)?!0:(t.append(rt(T,_,o),a(h)),!1)}const f=[],p=Object.assign(fn,{defaultVisitor:c,convertValue:a,isVisitable:ge});function m(h,_){if(!l.isUndefined(h)){if(f.indexOf(h)!==-1)throw Error("Circular reference detected in "+_.join("."));f.push(h),l.forEach(h,function(R,N){(!(l.isUndefined(R)||R===null)&&s.call(t,R,l.isString(N)?N.trim():N,_,p))===!0&&m(R,_?_.concat(N):[N])}),f.pop()}}if(!l.isObject(e))throw new TypeError("data must be an object");return m(e),t}function st(e){const t={"!":"%21","'":"%27","(":"%28",")":"%29","~":"%7E","%20":"+","%00":"\0"};return encodeURIComponent(e).replace(/[!'()~]|%20|%00/g,function(r){return t[r]})}function Se(e,t){this._pairs=[],e&&se(e,this,t)}const ot=Se.prototype;ot.append=function(t,n){this._pairs.push([t,n])},ot.toString=function(t){const n=t?function(r){return t.call(this,r,st)}:st;return this._pairs.map(function(s){return n(s[0])+"="+n(s[1])},"").join("&")};function pn(e){return encodeURIComponent(e).replace(/%3A/gi,":").replace(/%24/g,"$").replace(/%2C/gi,",").replace(/%20/g,"+").replace(/%5B/gi,"[").replace(/%5D/gi,"]")}function it(e,t,n){if(!t)return e;const r=n&&n.encode||pn,s=n&&n.serialize;let o;if(s?o=s(t,n):o=l.isURLSearchParams(t)?t.toString():new Se(t,n).toString(r),o){const i=e.indexOf("#");i!==-1&&(e=e.slice(0,i)),e+=(e.indexOf("?")===-1?"?":"&")+o}return e}class hn{constructor(){this.handlers=[]}use(t,n,r){return this.handlers.push({fulfilled:t,rejected:n,synchronous:r?r.synchronous:!1,runWhen:r?r.runWhen:null}),this.handlers.length-1}eject(t){this.handlers[t]&&(this.handlers[t]=null)}clear(){this.handlers&&(this.handlers=[])}forEach(t){l.forEach(this.handlers,function(r){r!==null&&t(r)})}}const at=hn,lt={silentJSONParsing:!0,forcedJSONParsing:!0,clarifyTimeoutError:!1},mn=typeof URLSearchParams<"u"?URLSearchParams:Se,_n=FormData,yn=(()=>{let e;return typeof navigator<"u"&&((e=navigator.product)==="ReactNative"||e==="NativeScript"||e==="NS")?!1:typeof window<"u"&&typeof document<"u"})(),bn=(()=>typeof WorkerGlobalScope<"u"&&self instanceof WorkerGlobalScope&&typeof self.importScripts=="function")(),C={isBrowser:!0,classes:{URLSearchParams:mn,FormData:_n,Blob},isStandardBrowserEnv:yn,isStandardBrowserWebWorkerEnv:bn,protocols:["http","https","file","blob","url","data"]};function En(e,t){return se(e,new C.classes.URLSearchParams,Object.assign({visitor:function(n,r,s,o){return C.isNode&&l.isBuffer(n)?(this.append(r,n.toString("base64")),!1):o.defaultVisitor.apply(this,arguments)}},t))}function wn(e){return l.matchAll(/\w+|\[(\w*)]/g,e).map(t=>t[0]==="[]"?"":t[1]||t[0])}function On(e){const t={},n=Object.keys(e);let r;const s=n.length;let o;for(r=0;r<s;r++)o=n[r],t[o]=e[o];return t}function ut(e){function t(n,r,s,o){let i=n[o++];const u=Number.isFinite(+i),d=o>=n.length;return i=!i&&l.isArray(s)?s.length:i,d?(l.hasOwnProp(s,i)?s[i]=[s[i],r]:s[i]=r,!u):((!s[i]||!l.isObject(s[i]))&&(s[i]=[]),t(n,r,s[i],o)&&l.isArray(s[i])&&(s[i]=On(s[i])),!u)}if(l.isFormData(e)&&l.isFunction(e.entries)){const n={};return l.forEachEntry(e,(r,s)=>{t(wn(r),s,n,0)}),n}return null}const gn={"Content-Type":void 0};function Sn(e,t,n){if(l.isString(e))try{return(t||JSON.parse)(e),l.trim(e)}catch(r){if(r.name!=="SyntaxError")throw r}return(n||JSON.stringify)(e)}const oe={transitional:lt,adapter:["xhr","http"],transformRequest:[function(t,n){const r=n.getContentType()||"",s=r.indexOf("application/json")>-1,o=l.isObject(t);if(o&&l.isHTMLForm(t)&&(t=new FormData(t)),l.isFormData(t))return s&&s?JSON.stringify(ut(t)):t;if(l.isArrayBuffer(t)||l.isBuffer(t)||l.isStream(t)||l.isFile(t)||l.isBlob(t))return t;if(l.isArrayBufferView(t))return t.buffer;if(l.isURLSearchParams(t))return n.setContentType("application/x-www-form-urlencoded;charset=utf-8",!1),t.toString();let u;if(o){if(r.indexOf("application/x-www-form-urlencoded")>-1)return En(t,this.formSerializer).toString();if((u=l.isFileList(t))||r.indexOf("multipart/form-data")>-1){const d=this.env&&this.env.FormData;return se(u?{"files[]":t}:t,d&&new d,this.formSerializer)}}return o||s?(n.setContentType("application/json",!1),Sn(t)):t}],transformResponse:[function(t){const n=this.transitional||oe.transitional,r=n&&n.forcedJSONParsing,s=this.responseType==="json";if(t&&l.isString(t)&&(r&&!this.responseType||s)){const i=!(n&&n.silentJSONParsing)&&s;try{return JSON.parse(t)}catch(u){if(i)throw u.name==="SyntaxError"?b.from(u,b.ERR_BAD_RESPONSE,this,null,this.response):u}}return t}],timeout:0,xsrfCookieName:"XSRF-TOKEN",xsrfHeaderName:"X-XSRF-TOKEN",maxContentLength:-1,maxBodyLength:-1,env:{FormData:C.classes.FormData,Blob:C.classes.Blob},validateStatus:function(t){return t>=200&&t<300},headers:{common:{Accept:"application/json, text/plain, */*"}}};l.forEach(["delete","get","head"],function(t){oe.headers[t]={}}),l.forEach(["post","put","patch"],function(t){oe.headers[t]=l.merge(gn)});const Re=oe,Rn=l.toObjectSet(["age","authorization","content-length","content-type","etag","expires","from","host","if-modified-since","if-unmodified-since","last-modified","location","max-forwards","proxy-authorization","referer","retry-after","user-agent"]),An=e=>{const t={};let n,r,s;return e&&e.split(`
`).forEach(function(i){s=i.indexOf(":"),n=i.substring(0,s).trim().toLowerCase(),r=i.substring(s+1).trim(),!(!n||t[n]&&Rn[n])&&(n==="set-cookie"?t[n]?t[n].push(r):t[n]=[r]:t[n]=t[n]?t[n]+", "+r:r)}),t},ct=Symbol("internals");function X(e){return e&&String(e).trim().toLowerCase()}function ie(e){return e===!1||e==null?e:l.isArray(e)?e.map(ie):String(e)}function Tn(e){const t=Object.create(null),n=/([^\s,;=]+)\s*(?:=\s*([^,;]+))?/g;let r;for(;r=n.exec(e);)t[r[1]]=r[2];return t}function Nn(e){return/^[-_a-zA-Z]+$/.test(e.trim())}function ft(e,t,n,r){if(l.isFunction(r))return r.call(this,t,n);if(!!l.isString(t)){if(l.isString(r))return t.indexOf(r)!==-1;if(l.isRegExp(r))return r.test(t)}}function kn(e){return e.trim().toLowerCase().replace(/([a-z\d])(\w*)/g,(t,n,r)=>n.toUpperCase()+r)}function Cn(e,t){const n=l.toCamelCase(" "+t);["get","set","has"].forEach(r=>{Object.defineProperty(e,r+n,{value:function(s,o,i){return this[r].call(this,t,s,o,i)},configurable:!0})})}class ae{constructor(t){t&&this.set(t)}set(t,n,r){const s=this;function o(u,d,a){const c=X(d);if(!c)throw new Error("header name must be a non-empty string");const f=l.findKey(s,c);(!f||s[f]===void 0||a===!0||a===void 0&&s[f]!==!1)&&(s[f||d]=ie(u))}const i=(u,d)=>l.forEach(u,(a,c)=>o(a,c,d));return l.isPlainObject(t)||t instanceof this.constructor?i(t,n):l.isString(t)&&(t=t.trim())&&!Nn(t)?i(An(t),n):t!=null&&o(n,t,r),this}get(t,n){if(t=X(t),t){const r=l.findKey(this,t);if(r){const s=this[r];if(!n)return s;if(n===!0)return Tn(s);if(l.isFunction(n))return n.call(this,s,r);if(l.isRegExp(n))return n.exec(s);throw new TypeError("parser must be boolean|regexp|function")}}}has(t,n){if(t=X(t),t){const r=l.findKey(this,t);return!!(r&&(!n||ft(this,this[r],r,n)))}return!1}delete(t,n){const r=this;let s=!1;function o(i){if(i=X(i),i){const u=l.findKey(r,i);u&&(!n||ft(r,r[u],u,n))&&(delete r[u],s=!0)}}return l.isArray(t)?t.forEach(o):o(t),s}clear(){return Object.keys(this).forEach(this.delete.bind(this))}normalize(t){const n=this,r={};return l.forEach(this,(s,o)=>{const i=l.findKey(r,o);if(i){n[i]=ie(s),delete n[o];return}const u=t?kn(o):String(o).trim();u!==o&&delete n[o],n[u]=ie(s),r[u]=!0}),this}concat(...t){return this.constructor.concat(this,...t)}toJSON(t){const n=Object.create(null);return l.forEach(this,(r,s)=>{r!=null&&r!==!1&&(n[s]=t&&l.isArray(r)?r.join(", "):r)}),n}[Symbol.iterator](){return Object.entries(this.toJSON())[Symbol.iterator]()}toString(){return Object.entries(this.toJSON()).map(([t,n])=>t+": "+n).join(`
`)}get[Symbol.toStringTag](){return"AxiosHeaders"}static from(t){return t instanceof this?t:new this(t)}static concat(t,...n){const r=new this(t);return n.forEach(s=>r.set(s)),r}static accessor(t){const r=(this[ct]=this[ct]={accessors:{}}).accessors,s=this.prototype;function o(i){const u=X(i);r[u]||(Cn(s,i),r[u]=!0)}return l.isArray(t)?t.forEach(o):o(t),this}}ae.accessor(["Content-Type","Content-Length","Accept","Accept-Encoding","User-Agent"]),l.freezeMethods(ae.prototype),l.freezeMethods(ae);const U=ae;function Ae(e,t){const n=this||Re,r=t||n,s=U.from(r.headers);let o=r.data;return l.forEach(e,function(u){o=u.call(n,o,s.normalize(),t?t.status:void 0)}),s.normalize(),o}function dt(e){return!!(e&&e.__CANCEL__)}function G(e,t,n){b.call(this,e==null?"canceled":e,b.ERR_CANCELED,t,n),this.name="CanceledError"}l.inherits(G,b,{__CANCEL__:!0});const Pn=null;function Fn(e,t,n){const r=n.config.validateStatus;!n.status||!r||r(n.status)?e(n):t(new b("Request failed with status code "+n.status,[b.ERR_BAD_REQUEST,b.ERR_BAD_RESPONSE][Math.floor(n.status/100)-4],n.config,n.request,n))}const Dn=C.isStandardBrowserEnv?function(){return{write:function(n,r,s,o,i,u){const d=[];d.push(n+"="+encodeURIComponent(r)),l.isNumber(s)&&d.push("expires="+new Date(s).toGMTString()),l.isString(o)&&d.push("path="+o),l.isString(i)&&d.push("domain="+i),u===!0&&d.push("secure"),document.cookie=d.join("; ")},read:function(n){const r=document.cookie.match(new RegExp("(^|;\\s*)("+n+")=([^;]*)"));return r?decodeURIComponent(r[3]):null},remove:function(n){this.write(n,"",Date.now()-864e5)}}}():function(){return{write:function(){},read:function(){return null},remove:function(){}}}();function Un(e){return/^([a-z][a-z\d+\-.]*:)?\/\//i.test(e)}function Bn(e,t){return t?e.replace(/\/+$/,"")+"/"+t.replace(/^\/+/,""):e}function pt(e,t){return e&&!Un(t)?Bn(e,t):t}const Ln=C.isStandardBrowserEnv?function(){const t=/(msie|trident)/i.test(navigator.userAgent),n=document.createElement("a");let r;function s(o){let i=o;return t&&(n.setAttribute("href",i),i=n.href),n.setAttribute("href",i),{href:n.href,protocol:n.protocol?n.protocol.replace(/:$/,""):"",host:n.host,search:n.search?n.search.replace(/^\?/,""):"",hash:n.hash?n.hash.replace(/^#/,""):"",hostname:n.hostname,port:n.port,pathname:n.pathname.charAt(0)==="/"?n.pathname:"/"+n.pathname}}return r=s(window.location.href),function(i){const u=l.isString(i)?s(i):i;return u.protocol===r.protocol&&u.host===r.host}}():function(){return function(){return!0}}();function xn(e){const t=/^([-+\w]{1,25})(:?\/\/|:)/.exec(e);return t&&t[1]||""}function jn(e,t){e=e||10;const n=new Array(e),r=new Array(e);let s=0,o=0,i;return t=t!==void 0?t:1e3,function(d){const a=Date.now(),c=r[o];i||(i=a),n[s]=d,r[s]=a;let f=o,p=0;for(;f!==s;)p+=n[f++],f=f%e;if(s=(s+1)%e,s===o&&(o=(o+1)%e),a-i<t)return;const m=c&&a-c;return m?Math.round(p*1e3/m):void 0}}function ht(e,t){let n=0;const r=jn(50,250);return s=>{const o=s.loaded,i=s.lengthComputable?s.total:void 0,u=o-n,d=r(u),a=o<=i;n=o;const c={loaded:o,total:i,progress:i?o/i:void 0,bytes:u,rate:d||void 0,estimated:d&&i&&a?(i-o)/d:void 0,event:s};c[t?"download":"upload"]=!0,e(c)}}const le={http:Pn,xhr:typeof XMLHttpRequest<"u"&&function(e){return new Promise(function(n,r){let s=e.data;const o=U.from(e.headers).normalize(),i=e.responseType;let u;function d(){e.cancelToken&&e.cancelToken.unsubscribe(u),e.signal&&e.signal.removeEventListener("abort",u)}l.isFormData(s)&&(C.isStandardBrowserEnv||C.isStandardBrowserWebWorkerEnv)&&o.setContentType(!1);let a=new XMLHttpRequest;if(e.auth){const m=e.auth.username||"",h=e.auth.password?unescape(encodeURIComponent(e.auth.password)):"";o.set("Authorization","Basic "+btoa(m+":"+h))}const c=pt(e.baseURL,e.url);a.open(e.method.toUpperCase(),it(c,e.params,e.paramsSerializer),!0),a.timeout=e.timeout;function f(){if(!a)return;const m=U.from("getAllResponseHeaders"in a&&a.getAllResponseHeaders()),_={data:!i||i==="text"||i==="json"?a.responseText:a.response,status:a.status,statusText:a.statusText,headers:m,config:e,request:a};Fn(function(R){n(R),d()},function(R){r(R),d()},_),a=null}if("onloadend"in a?a.onloadend=f:a.onreadystatechange=function(){!a||a.readyState!==4||a.status===0&&!(a.responseURL&&a.responseURL.indexOf("file:")===0)||setTimeout(f)},a.onabort=function(){!a||(r(new b("Request aborted",b.ECONNABORTED,e,a)),a=null)},a.onerror=function(){r(new b("Network Error",b.ERR_NETWORK,e,a)),a=null},a.ontimeout=function(){let h=e.timeout?"timeout of "+e.timeout+"ms exceeded":"timeout exceeded";const _=e.transitional||lt;e.timeoutErrorMessage&&(h=e.timeoutErrorMessage),r(new b(h,_.clarifyTimeoutError?b.ETIMEDOUT:b.ECONNABORTED,e,a)),a=null},C.isStandardBrowserEnv){const m=(e.withCredentials||Ln(c))&&e.xsrfCookieName&&Dn.read(e.xsrfCookieName);m&&o.set(e.xsrfHeaderName,m)}s===void 0&&o.setContentType(null),"setRequestHeader"in a&&l.forEach(o.toJSON(),function(h,_){a.setRequestHeader(_,h)}),l.isUndefined(e.withCredentials)||(a.withCredentials=!!e.withCredentials),i&&i!=="json"&&(a.responseType=e.responseType),typeof e.onDownloadProgress=="function"&&a.addEventListener("progress",ht(e.onDownloadProgress,!0)),typeof e.onUploadProgress=="function"&&a.upload&&a.upload.addEventListener("progress",ht(e.onUploadProgress)),(e.cancelToken||e.signal)&&(u=m=>{!a||(r(!m||m.type?new G(null,e,a):m),a.abort(),a=null)},e.cancelToken&&e.cancelToken.subscribe(u),e.signal&&(e.signal.aborted?u():e.signal.addEventListener("abort",u)));const p=xn(c);if(p&&C.protocols.indexOf(p)===-1){r(new b("Unsupported protocol "+p+":",b.ERR_BAD_REQUEST,e));return}a.send(s||null)})}};l.forEach(le,(e,t)=>{if(e){try{Object.defineProperty(e,"name",{value:t})}catch{}Object.defineProperty(e,"adapterName",{value:t})}});const Hn={getAdapter:e=>{e=l.isArray(e)?e:[e];const{length:t}=e;let n,r;for(let s=0;s<t&&(n=e[s],!(r=l.isString(n)?le[n.toLowerCase()]:n));s++);if(!r)throw r===!1?new b(`Adapter ${n} is not supported by the environment`,"ERR_NOT_SUPPORT"):new Error(l.hasOwnProp(le,n)?`Adapter '${n}' is not available in the build`:`Unknown adapter '${n}'`);if(!l.isFunction(r))throw new TypeError("adapter is not a function");return r},adapters:le};function Te(e){if(e.cancelToken&&e.cancelToken.throwIfRequested(),e.signal&&e.signal.aborted)throw new G(null,e)}function mt(e){return Te(e),e.headers=U.from(e.headers),e.data=Ae.call(e,e.transformRequest),["post","put","patch"].indexOf(e.method)!==-1&&e.headers.setContentType("application/x-www-form-urlencoded",!1),Hn.getAdapter(e.adapter||Re.adapter)(e).then(function(r){return Te(e),r.data=Ae.call(e,e.transformResponse,r),r.headers=U.from(r.headers),r},function(r){return dt(r)||(Te(e),r&&r.response&&(r.response.data=Ae.call(e,e.transformResponse,r.response),r.response.headers=U.from(r.response.headers))),Promise.reject(r)})}const _t=e=>e instanceof U?e.toJSON():e;function I(e,t){t=t||{};const n={};function r(a,c,f){return l.isPlainObject(a)&&l.isPlainObject(c)?l.merge.call({caseless:f},a,c):l.isPlainObject(c)?l.merge({},c):l.isArray(c)?c.slice():c}function s(a,c,f){if(l.isUndefined(c)){if(!l.isUndefined(a))return r(void 0,a,f)}else return r(a,c,f)}function o(a,c){if(!l.isUndefined(c))return r(void 0,c)}function i(a,c){if(l.isUndefined(c)){if(!l.isUndefined(a))return r(void 0,a)}else return r(void 0,c)}function u(a,c,f){if(f in t)return r(a,c);if(f in e)return r(void 0,a)}const d={url:o,method:o,data:o,baseURL:i,transformRequest:i,transformResponse:i,paramsSerializer:i,timeout:i,timeoutMessage:i,withCredentials:i,adapter:i,responseType:i,xsrfCookieName:i,xsrfHeaderName:i,onUploadProgress:i,onDownloadProgress:i,decompress:i,maxContentLength:i,maxBodyLength:i,beforeRedirect:i,transport:i,httpAgent:i,httpsAgent:i,cancelToken:i,socketPath:i,responseEncoding:i,validateStatus:u,headers:(a,c)=>s(_t(a),_t(c),!0)};return l.forEach(Object.keys(e).concat(Object.keys(t)),function(c){const f=d[c]||s,p=f(e[c],t[c],c);l.isUndefined(p)&&f!==u||(n[c]=p)}),n}const yt="1.2.1",Ne={};["object","boolean","number","function","string","symbol"].forEach((e,t)=>{Ne[e]=function(r){return typeof r===e||"a"+(t<1?"n ":" ")+e}});const bt={};Ne.transitional=function(t,n,r){function s(o,i){return"[Axios v"+yt+"] Transitional option '"+o+"'"+i+(r?". "+r:"")}return(o,i,u)=>{if(t===!1)throw new b(s(i," has been removed"+(n?" in "+n:"")),b.ERR_DEPRECATED);return n&&!bt[i]&&(bt[i]=!0,console.warn(s(i," has been deprecated since v"+n+" and will be removed in the near future"))),t?t(o,i,u):!0}};function Mn(e,t,n){if(typeof e!="object")throw new b("options must be an object",b.ERR_BAD_OPTION_VALUE);const r=Object.keys(e);let s=r.length;for(;s-- >0;){const o=r[s],i=t[o];if(i){const u=e[o],d=u===void 0||i(u,o,e);if(d!==!0)throw new b("option "+o+" must be "+d,b.ERR_BAD_OPTION_VALUE);continue}if(n!==!0)throw new b("Unknown option "+o,b.ERR_BAD_OPTION)}}const ke={assertOptions:Mn,validators:Ne},L=ke.validators;class ue{constructor(t){this.defaults=t,this.interceptors={request:new at,response:new at}}request(t,n){typeof t=="string"?(n=n||{},n.url=t):n=t||{},n=I(this.defaults,n);const{transitional:r,paramsSerializer:s,headers:o}=n;r!==void 0&&ke.assertOptions(r,{silentJSONParsing:L.transitional(L.boolean),forcedJSONParsing:L.transitional(L.boolean),clarifyTimeoutError:L.transitional(L.boolean)},!1),s!==void 0&&ke.assertOptions(s,{encode:L.function,serialize:L.function},!0),n.method=(n.method||this.defaults.method||"get").toLowerCase();let i;i=o&&l.merge(o.common,o[n.method]),i&&l.forEach(["delete","get","head","post","put","patch","common"],h=>{delete o[h]}),n.headers=U.concat(i,o);const u=[];let d=!0;this.interceptors.request.forEach(function(_){typeof _.runWhen=="function"&&_.runWhen(n)===!1||(d=d&&_.synchronous,u.unshift(_.fulfilled,_.rejected))});const a=[];this.interceptors.response.forEach(function(_){a.push(_.fulfilled,_.rejected)});let c,f=0,p;if(!d){const h=[mt.bind(this),void 0];for(h.unshift.apply(h,u),h.push.apply(h,a),p=h.length,c=Promise.resolve(n);f<p;)c=c.then(h[f++],h[f++]);return c}p=u.length;let m=n;for(f=0;f<p;){const h=u[f++],_=u[f++];try{m=h(m)}catch(T){_.call(this,T);break}}try{c=mt.call(this,m)}catch(h){return Promise.reject(h)}for(f=0,p=a.length;f<p;)c=c.then(a[f++],a[f++]);return c}getUri(t){t=I(this.defaults,t);const n=pt(t.baseURL,t.url);return it(n,t.params,t.paramsSerializer)}}l.forEach(["delete","get","head","options"],function(t){ue.prototype[t]=function(n,r){return this.request(I(r||{},{method:t,url:n,data:(r||{}).data}))}}),l.forEach(["post","put","patch"],function(t){function n(r){return function(o,i,u){return this.request(I(u||{},{method:t,headers:r?{"Content-Type":"multipart/form-data"}:{},url:o,data:i}))}}ue.prototype[t]=n(),ue.prototype[t+"Form"]=n(!0)});const ce=ue;class Ce{constructor(t){if(typeof t!="function")throw new TypeError("executor must be a function.");let n;this.promise=new Promise(function(o){n=o});const r=this;this.promise.then(s=>{if(!r._listeners)return;let o=r._listeners.length;for(;o-- >0;)r._listeners[o](s);r._listeners=null}),this.promise.then=s=>{let o;const i=new Promise(u=>{r.subscribe(u),o=u}).then(s);return i.cancel=function(){r.unsubscribe(o)},i},t(function(o,i,u){r.reason||(r.reason=new G(o,i,u),n(r.reason))})}throwIfRequested(){if(this.reason)throw this.reason}subscribe(t){if(this.reason){t(this.reason);return}this._listeners?this._listeners.push(t):this._listeners=[t]}unsubscribe(t){if(!this._listeners)return;const n=this._listeners.indexOf(t);n!==-1&&this._listeners.splice(n,1)}static source(){let t;return{token:new Ce(function(s){t=s}),cancel:t}}}const vn=Ce;function In(e){return function(n){return e.apply(null,n)}}function zn(e){return l.isObject(e)&&e.isAxiosError===!0}function Et(e){const t=new ce(e),n=Ve(ce.prototype.request,t);return l.extend(n,ce.prototype,t,{allOwnKeys:!0}),l.extend(n,t,null,{allOwnKeys:!0}),n.create=function(s){return Et(I(e,s))},n}const g=Et(Re);g.Axios=ce,g.CanceledError=G,g.CancelToken=vn,g.isCancel=dt,g.VERSION=yt,g.toFormData=se,g.AxiosError=b,g.Cancel=g.CanceledError,g.all=function(t){return Promise.all(t)},g.spread=In,g.isAxiosError=zn,g.mergeConfig=I,g.AxiosHeaders=U,g.formToJSON=e=>ut(l.isHTMLForm(e)?new FormData(e):e),g.default=g;const Jn=g,Or="";function wt(e){let t,n,r,s,o,i;function u(c,f){return!c[4]&&!c[5]&&!c[6]?Vn:qn}let d=u(e),a=d(e);return{c(){t=O("div"),n=O("div"),a.c(),r=F(),s=O("input"),y(n,"id","widget-label"),y(n,"class","svelte-1f4196f"),y(s,"id","fileUpload"),y(s,"type","file"),y(s,"class","svelte-1f4196f"),y(t,"id","fileUploadWidget"),y(t,"class","svelte-1f4196f")},m(c,f){A(c,t,f),E(t,n),a.m(n,null),E(t,r),E(t,s),o||(i=[M(s,"change",e[18]),M(s,"change",e[11])],o=!0)},p(c,f){d===(d=u(c))&&a?a.p(c,f):(a.d(1),a=d(c),a&&(a.c(),a.m(n,null)))},d(c){c&&S(t),a.d(),o=!1,H(i)}}}function qn(e){let t,n,r,s,o,i=`${e[3]}%`;function u(f,p){return f[5]?Wn:Kn}let d=u(e),a=d(e),c=e[6]&&gt();return{c(){t=O("div"),n=O("div"),a.c(),r=F(),c&&c.c(),s=F(),o=O("div"),y(n,"class","percentage-text svelte-1f4196f"),y(o,"id","percentage-bar"),y(o,"class","svelte-1f4196f"),xe(o,"width",i),y(t,"id","percentage"),y(t,"class","svelte-1f4196f")},m(f,p){A(f,t,p),E(t,n),a.m(n,null),E(n,r),c&&c.m(n,null),E(t,s),E(t,o)},p(f,p){d===(d=u(f))&&a?a.p(f,p):(a.d(1),a=d(f),a&&(a.c(),a.m(n,r))),f[6]?c||(c=gt(),c.c(),c.m(n,null)):c&&(c.d(1),c=null),p&8&&i!==(i=`${f[3]}%`)&&xe(o,"width",i)},d(f){f&&S(t),a.d(),c&&c.d()}}}function Vn(e){let t;function n(o,i){return o[1]?Gn:Xn}let r=n(e),s=r(e);return{c(){s.c(),t=pe()},m(o,i){s.m(o,i),A(o,t,i)},p(o,i){r!==(r=n(o))&&(s.d(1),s=r(o),s&&(s.c(),s.m(t.parentNode,t)))},d(o){s.d(o),o&&S(t)}}}function Wn(e){let t;return{c(){t=B("Waiting for data schema detection...")},m(n,r){A(n,t,r)},p:k,d(n){n&&S(t)}}}function Kn(e){let t,n=!e[6]&&Ot(e);return{c(){n&&n.c(),t=pe()},m(r,s){n&&n.m(r,s),A(r,t,s)},p(r,s){r[6]?n&&(n.d(1),n=null):n?n.p(r,s):(n=Ot(r),n.c(),n.m(t.parentNode,t))},d(r){n&&n.d(r),r&&S(t)}}}function Ot(e){let t,n;return{c(){t=B(e[3]),n=B("%")},m(r,s){A(r,t,s),A(r,n,s)},p(r,s){s&8&&Nt(t,r[3])},d(r){r&&S(t),r&&S(n)}}}function gt(e){let t;return{c(){t=B("File uploaded")},m(n,r){A(n,t,r)},d(n){n&&S(t)}}}function Xn(e){let t;return{c(){t=B("Select a file to upload")},m(n,r){A(n,t,r)},d(n){n&&S(t)}}}function Gn(e){let t;return{c(){t=B("Select a file to replace the current one")},m(n,r){A(n,t,r)},d(n){n&&S(t)}}}function Qn(e){let t,n,r,s,o,i,u,d,a;return{c(){t=O("div"),n=O("label"),n.textContent="URL",r=F(),s=O("div"),o=O("input"),i=F(),u=O("input"),y(n,"class","control-label"),y(n,"for","field_url"),y(o,"id","field_url"),y(o,"class","form-control"),y(o,"type","text"),y(o,"name","url"),y(u,"type","hidden"),y(u,"name","clear_upload"),u.value="true",y(s,"class","controls"),y(t,"id","resourceURL"),y(t,"class","controls svelte-1f4196f")},m(c,f){A(c,t,f),E(t,n),E(t,r),E(t,s),E(s,o),Y(o,e[8]),E(s,i),E(s,u),d||(a=M(o,"input",e[20]),d=!0)},p(c,f){f&256&&o.value!==c[8]&&Y(o,c[8])},d(c){c&&S(t),d=!1,a()}}}function Yn(e){let t,n=e[9]!=""&&St(e);return{c(){n&&n.c(),t=pe()},m(r,s){n&&n.m(r,s),A(r,t,s)},p(r,s){r[9]!=""?n?n.p(r,s):(n=St(r),n.c(),n.m(t.parentNode,t)):n&&(n.d(1),n=null)},d(r){n&&n.d(r),r&&S(t)}}}function St(e){let t,n,r,s,o,i,u,d;return{c(){t=O("div"),n=O("label"),n.textContent="Current file",r=F(),s=O("div"),o=O("input"),y(n,"class","control-label"),y(n,"for","field_url"),o.readOnly=i=e[0]!="upload"?void 0:!0,y(o,"id","field_url"),y(o,"class","form-control"),y(o,"type","text"),y(o,"name","url"),y(s,"class","controls"),y(t,"class","controls")},m(a,c){A(a,t,c),E(t,n),E(t,r),E(t,s),E(s,o),Y(o,e[9]),u||(d=M(o,"input",e[19]),u=!0)},p(a,c){c&1&&i!==(i=a[0]!="upload"?void 0:!0)&&(o.readOnly=i),c&512&&o.value!==a[9]&&Y(o,a[9])},d(a){a&&S(t),u=!1,d()}}}function Zn(e){let t,n,r,s,o,i,u,d,a=e[7]=="upload"&&wt(e);function c(m,h){if(m[7]=="upload")return Yn;if(m[7]!="None")return Qn}let f=c(e),p=f&&f(e);return{c(){t=O("div"),n=O("a"),n.innerHTML='<i class="fa fa-cloud-upload"></i>File',r=F(),s=O("a"),s.innerHTML='<i class="fa fa-globe"></i>Link',o=F(),a&&a.c(),i=F(),p&&p.c(),y(n,"class","btn btn-default"),Z(n,"active",e[7]=="upload"),y(s,"class","btn btn-default"),Z(s,"active",e[7]!="upload"&&e[7]!="None"),y(t,"class","form-group")},m(m,h){A(m,t,h),E(t,n),E(t,r),E(t,s),E(t,o),a&&a.m(t,null),E(t,i),p&&p.m(t,null),u||(d=[M(n,"click",e[16]),M(s,"click",e[17])],u=!0)},p(m,[h]){h&128&&Z(n,"active",m[7]=="upload"),h&128&&Z(s,"active",m[7]!="upload"&&m[7]!="None"),m[7]=="upload"?a?a.p(m,h):(a=wt(m),a.c(),a.m(t,i)):a&&(a.d(1),a=null),f===(f=c(m))&&p?p.p(m,h):(p&&p.d(1),p=f&&f(m),p&&(p.c(),p.m(t,null)))},i:k,o:k,d(m){m&&S(t),a&&a.d(),p&&p.d(),u=!1,H(d)}}}function Rt(e){let t=e.split("/");return t.length>0?t[t.length-1]:t[0]}function $n(e,t,n){let{upload_url:r}=t,{dataset_id:s}=t,{resource_id:o}=t,{update:i=""}=t,{current_url:u}=t,{url_type:d=""}=t,a,c=0,f=!1,p=!1,m=!1,h=je(),_=i?"update":"create",T=d,R="",N="";d!="upload"?R=u:N=Rt(u);async function z(w,Q){try{const P={onUploadProgress:fr=>{const{loaded:dr,total:pr}=fr,De=Math.floor(dr*100/pr);De<=100&&(Q(De),De==100&&(n(4,f=!1),n(5,p=!0)))}},de=_=="update"?`${r}/dataset/${s}/resource/${o}/file`:`${r}/dataset/${s}/resource/file`,{data:Fe}=await Jn.post(de,w,P);return Fe}catch(P){console.log("ERROR",P.message)}}function fe(w){n(3,c=w)}function Pe(w){n(7,T=w)}async function or(w){try{const Q=w.target.files[0],P=new FormData;P.append("upload",Q),P.append("package_id",s),i&&(P.append("id",o),P.append("clear_upload",!0),P.append("url_type",d)),n(4,f=!0);let de=await z(P,fe),Fe={data:de};n(9,N=Rt(de.url)),n(0,d="upload"),h("fileUploaded",Fe),n(5,p=!1),n(6,m=!0)}catch(Q){console.log("ERROR",Q),fe(0)}}const ir=w=>{Pe("upload")},ar=w=>{Pe("")};function lr(){a=this.files,n(2,a)}function ur(){N=this.value,n(9,N)}function cr(){R=this.value,n(8,R)}return e.$$set=w=>{"upload_url"in w&&n(12,r=w.upload_url),"dataset_id"in w&&n(13,s=w.dataset_id),"resource_id"in w&&n(14,o=w.resource_id),"update"in w&&n(1,i=w.update),"current_url"in w&&n(15,u=w.current_url),"url_type"in w&&n(0,d=w.url_type)},[d,i,a,c,f,p,m,T,R,N,Pe,or,r,s,o,u,ir,ar,lr,ur,cr]}class er extends qe{constructor(t){super(),Je(this,t,$n,Zn,Le,{upload_url:12,dataset_id:13,resource_id:14,update:1,current_url:15,url_type:0})}}function tr(e){let t,n,r;return n=new er({props:{upload_url:e[0],dataset_id:e[1],resource_id:e[2],update:e[3],current_url:e[4],url_type:e[5]}}),n.$on("fileUploaded",e[7]),{c(){t=O("main"),Lt(n.$$.fragment)},m(s,o){A(s,t,o),Ie(n,t,null),e[8](t),r=!0},p(s,[o]){const i={};o&1&&(i.upload_url=s[0]),o&2&&(i.dataset_id=s[1]),o&4&&(i.resource_id=s[2]),o&8&&(i.update=s[3]),o&16&&(i.current_url=s[4]),o&32&&(i.url_type=s[5]),n.$set(i)},i(s){r||(ve(n.$$.fragment,s),r=!0)},o(s){Bt(n.$$.fragment,s),r=!1},d(s){s&&S(t),ze(n),e[8](null)}}}function nr(e,t,n){let{upload_url:r}=t,{dataset_id:s}=t,{resource_id:o}=t,{update:i}=t,{current_url:u}=t,{url_type:d}=t;je();let a;function c(p){a.parentNode.dispatchEvent(new CustomEvent("fileUploaded",{detail:p.detail.data}))}function f(p){he[p?"unshift":"push"](()=>{a=p,n(6,a)})}return e.$$set=p=>{"upload_url"in p&&n(0,r=p.upload_url),"dataset_id"in p&&n(1,s=p.dataset_id),"resource_id"in p&&n(2,o=p.resource_id),"update"in p&&n(3,i=p.update),"current_url"in p&&n(4,u=p.current_url),"url_type"in p&&n(5,d=p.url_type)},[r,s,o,i,u,d,a,c,f]}class rr extends qe{constructor(t){super(),Je(this,t,nr,tr,Le,{upload_url:0,dataset_id:1,resource_id:2,update:3,current_url:4,url_type:5})}}function sr(e,t="",n="",r="",s="",o="",i=""){new rr({target:document.getElementById(e),props:{upload_url:t,dataset_id:n,resource_id:r,url_type:s,current_url:o,update:i}})}return sr});
