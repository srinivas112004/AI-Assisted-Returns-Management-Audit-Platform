import React from 'react';
import { ShieldCheck, Bell, Database } from 'lucide-react';
import { NavLink } from 'react-router-dom';

export const Navbar: React.FC = () => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            System Workspace
          </span>
        </div>
        <span className="text-slate-300">/</span>
        <span className="text-xs font-medium text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
          Anchor Seed: 20261022
        </span>
      </div>

      <div className="flex items-center gap-4">
        <NavLink
          to="/generator"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-blue-600 bg-slate-50 hover:bg-blue-50 px-3 py-1.5 rounded-md border border-slate-200 transition-colors"
        >
          <Database className="w-3.5 h-3.5 text-blue-600" />
          <span>Generator</span>
        </NavLink>

        <div className="h-4 w-px bg-slate-200"></div>

        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-semibold text-xs border border-blue-200">
            QA
          </div>
          <div className="text-left hidden sm:block">
            <span className="text-xs font-semibold text-slate-900 block leading-tight">Senior QA / Auditor</span>
            <span className="text-[10px] text-emerald-600 font-medium flex items-center gap-1 leading-tight">
              <ShieldCheck className="w-3 h-3 inline" /> Admin Policy Token
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

