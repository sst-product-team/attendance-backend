function e(e,s,a,l){Object.defineProperty(e,s,{get:a,set:l,enumerable:!0,configurable:!0})}var s=globalThis.parcelRequire2e1e,a=s.register;a("jm23Y",function(a,l){Object.defineProperty(a.exports,"__esModule",{value:!0,configurable:!0}),e(a.exports,"default",()=>c);var t=s("ayMG0"),r=s("8oTda"),c=({allAttendance:e,classDetails:s})=>(0,t.jsxs)("div",{children:[(0,t.jsx)("div",{className:"flex justify-between",children:(0,t.jsx)(r.default,{student:!0,classDetails:s})}),(0,t.jsx)("div",{className:"h-full w-full",children:(0,t.jsxs)("table",{className:"w-full mt-8 text-left bg-white border border-gray-300",children:[(0,t.jsx)("thead",{className:"bg-gray-200 sticky top-0 z-40",children:(0,t.jsxs)("tr",{children:[(0,t.jsx)("th",{className:"py-2",children:"#"}),(0,t.jsx)("th",{className:"py-2",children:"Name"}),(0,t.jsx)("th",{className:"py-2",children:"Email"}),(0,t.jsx)("th",{className:"py-2",children:"Attendance"})]})}),(0,t.jsx)("tbody",{className:"overflow-y-scroll",children:e.map((e,s)=>{var a;return(0,t.jsxs)("tr",{className:s%2==0?"bg-gray-100":"bg-white",children:[(0,t.jsx)("td",{className:"py-2",children:s+1}),(0,t.jsx)("td",{className:"py-2",children:e.name}),(0,t.jsx)("td",{className:"py-2",children:e.mail}),(0,t.jsx)("td",{className:"py-2 pr-2",children:(0,t.jsx)("div",{className:"flex justify-between",children:(0,t.jsx)("span",{className:`${"Present"===(a=e.status)?"text-sky-700":"Absent"===a?"text-red-700":"Proxy"===a?"text-red-950":""}`,children:e.status})})})]},e.mail)})})]})})]})}),a("8oTda",function(a,l){e(a.exports,"default",()=>n);var t=s("ayMG0");s("acw62");var r=s("jEyqx"),c=s("8Qx3l"),n=({classDetails:e,student:s})=>(0,t.jsxs)("div",{className:"w-full flex justify-between",children:[(0,t.jsx)("h2",{className:"text-3xl font-medium",children:e.name}),(0,t.jsxs)("div",{className:"flex justify-evenly gap-4",children:[s&&(0,t.jsxs)("a",{className:"text-blue-600",href:"/accounts/login",children:[(0,t.jsx)(r.FontAwesomeIcon,{icon:c.faLink,size:"1x",color:"blue"}),"login"]}),s&&(0,t.jsx)("p",{children:"This page is updated every 5 min"}),s||(0,t.jsxs)("a",{href:`${getAttendanceURL+"download/"}`,className:"px-4 py-2 text-sm font-medium text-gray-900 bg-gray-300 border rounded-s-lg hover:bg-gray-100 hover:text-blue-700",children:[(0,t.jsx)(r.FontAwesomeIcon,{icon:c.faDownload,size:"1x",color:"blue"}),"Export to CSV"]})]})]})});
//# sourceMappingURL=StudentPage.635e54b1.js.map
