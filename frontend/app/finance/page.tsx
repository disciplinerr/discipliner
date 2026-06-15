"use client";

import { useCallback, useEffect, useState } from "react";
import AddBillModal from "@/components/finance/AddBillModal";
import AddGoalModal from "@/components/finance/AddGoalModal";
import AddIncomeModal from "@/components/finance/AddIncomeModal";
import AddInstallmentModal from "@/components/finance/AddInstallmentModal";
import AddTransactionModal from "@/components/finance/AddTransactionModal";
import BillsList from "@/components/finance/BillsList";
import IncomeList from "@/components/finance/IncomeList";
import CategoryBudgets from "@/components/finance/CategoryBudgets";
import CategoryManagerModal from "@/components/finance/CategoryManagerModal";
import InstallmentsList from "@/components/finance/InstallmentsList";
import MonthSelector from "@/components/finance/MonthSelector";
import RuleBreakdown from "@/components/finance/RuleBreakdown";
import SavingsGoals from "@/components/finance/SavingsGoals";
import SummaryCards from "@/components/finance/SummaryCards";
import TransactionList from "@/components/finance/TransactionList";
import TrendChart from "@/components/finance/TrendChart";
import Card from "@/components/ui/Card";
import RequireAuth from "@/components/ui/RequireAuth";
import {
  getBillsForMonth,
  getCategories,
  getFinanceOverview,
  getGoals,
  getIncomes,
  getInstallmentsForMonth,
  getTransactions,
  getTrend,
} from "@/lib/api";
import { formatMoney } from "@/lib/finance";
import { useI18n } from "@/lib/i18n";
import {
  BillStatus,
  Category,
  FinanceOverview,
  InstallmentStatus,
  RecurringIncome,
  SavingsGoal,
  Transaction,
  TrendPoint,
} from "@/types";

const SMALL_BTN =
  "rounded-lg border border-line px-2.5 py-1 text-[11px] font-bold text-muted transition-colors hover:border-secondary hover:text-foreground";

export default function FinancePage() {
  const { t, locale } = useI18n();
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);

  const [overview, setOverview] = useState<FinanceOverview | null>(null);
  const [bills, setBills] = useState<BillStatus[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [installments, setInstallments] = useState<InstallmentStatus[]>([]);
  const [goals, setGoals] = useState<SavingsGoal[]>([]);
  const [incomes, setIncomes] = useState<RecurringIncome[]>([]);
  const [trend, setTrend] = useState<TrendPoint[]>([]);

  const [showTxn, setShowTxn] = useState(false);
  const [showBill, setShowBill] = useState(false);
  const [showCats, setShowCats] = useState(false);
  const [showInstallment, setShowInstallment] = useState(false);
  const [showGoal, setShowGoal] = useState(false);
  const [showIncome, setShowIncome] = useState(false);

  const load = useCallback(() => {
    getFinanceOverview(year, month).then(setOverview).catch(() => {});
    getBillsForMonth(year, month).then(setBills).catch(() => {});
    getTransactions(year, month).then(setTransactions).catch(() => {});
    getCategories().then(setCategories).catch(() => {});
    getInstallmentsForMonth(year, month).then(setInstallments).catch(() => {});
    getGoals().then(setGoals).catch(() => {});
    getIncomes().then(setIncomes).catch(() => {});
    getTrend(year, month, 6).then(setTrend).catch(() => {});
  }, [year, month]);

  useEffect(load, [load]);

  // A sensible default date for the transaction modal: today if we're on the
  // current month, otherwise the 1st of the selected month.
  const defaultDate =
    year === now.getFullYear() && month === now.getMonth() + 1
      ? now.toISOString().slice(0, 10)
      : `${year}-${String(month).padStart(2, "0")}-01`;

  return (
    <RequireAuth>
      <div className="space-y-6">
        <div className="animate-fade-up flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">{t("finance.title")}</h1>
            <p className="mt-1 text-secondary">{t("finance.subtitle")}</p>
          </div>
          <MonthSelector
            year={year}
            month={month}
            onChange={(y, m) => {
              setYear(y);
              setMonth(m);
            }}
          />
        </div>

        {overview ? (
          <>
            <SummaryCards data={overview} />

            <Card
              title={t("finance.incomes")}
              action={
                <div className="flex items-center gap-3">
                  <span className="text-xs font-bold text-emerald-400">
                    {formatMoney(overview.recurring_income, locale)}
                  </span>
                  <button type="button" className={SMALL_BTN} onClick={() => setShowIncome(true)}>
                    {t("finance.add_income")}
                  </button>
                </div>
              }
            >
              <IncomeList incomes={incomes} onChanged={load} />
            </Card>

            <Card
              title={t("finance.rule_503020")}
              action={
                <button type="button" className={SMALL_BTN} onClick={() => setShowCats(true)}>
                  {t("finance.manage_categories")}
                </button>
              }
            >
              <RuleBreakdown groups={overview.groups} income={overview.total_income} />
            </Card>

            <Card title={t("finance.budgets")}>
              <CategoryBudgets categories={overview.categories} />
            </Card>

            <Card
              title={t("finance.bills")}
              action={
                <div className="flex items-center gap-3">
                  <span className="text-xs font-bold text-secondary">
                    {formatMoney(overview.bills_paid, locale)} / {" "}
                    {formatMoney(overview.bills_total, locale)}
                    {overview.bills_overdue > 0 && (
                      <span className="ml-2 text-rose-400">
                        {overview.bills_overdue} {t("finance.bills_overdue")}
                      </span>
                    )}
                  </span>
                  <button type="button" className={SMALL_BTN} onClick={() => setShowBill(true)}>
                    {t("finance.add_bill")}
                  </button>
                </div>
              }
            >
              <BillsList bills={bills} year={year} month={month} onChanged={load} />
            </Card>

            <Card
              title={t("finance.installments")}
              action={
                <div className="flex items-center gap-3">
                  <span className="text-xs font-bold text-secondary">
                    {formatMoney(overview.installments_month, locale)}
                    <span className="text-muted">
                      {" "}
                      · {t("finance.installments_outstanding")}{" "}
                      {formatMoney(overview.installments_outstanding, locale)}
                    </span>
                  </span>
                  <button
                    type="button"
                    className={SMALL_BTN}
                    onClick={() => setShowInstallment(true)}
                  >
                    {t("finance.add_installment")}
                  </button>
                </div>
              }
            >
              <InstallmentsList installments={installments} onChanged={load} />
            </Card>

            <Card title={t("finance.trend")}>
              <TrendChart points={trend} />
            </Card>

            <Card
              title={t("finance.goals")}
              action={
                <button type="button" className={SMALL_BTN} onClick={() => setShowGoal(true)}>
                  {t("finance.add_goal")}
                </button>
              }
            >
              <SavingsGoals goals={goals} onChanged={load} />
            </Card>

            <Card
              title={t("finance.transactions")}
              action={
                <button type="button" className={SMALL_BTN} onClick={() => setShowTxn(true)}>
                  {t("finance.add_transaction")}
                </button>
              }
            >
              <TransactionList
                transactions={transactions}
                categories={categories}
                onChanged={load}
              />
            </Card>
          </>
        ) : (
          <p className="text-sm text-muted">{t("common.loading")}</p>
        )}
      </div>

      {showTxn && (
        <AddTransactionModal
          categories={categories}
          defaultDate={defaultDate}
          onClose={() => setShowTxn(false)}
          onSaved={load}
        />
      )}
      {showBill && (
        <AddBillModal
          categories={categories}
          onClose={() => setShowBill(false)}
          onSaved={load}
        />
      )}
      {showCats && (
        <CategoryManagerModal onClose={() => setShowCats(false)} onChanged={load} />
      )}
      {showInstallment && (
        <AddInstallmentModal
          categories={categories}
          defaultYear={year}
          defaultMonth={month}
          onClose={() => setShowInstallment(false)}
          onSaved={load}
        />
      )}
      {showGoal && (
        <AddGoalModal onClose={() => setShowGoal(false)} onSaved={load} />
      )}
      {showIncome && (
        <AddIncomeModal onClose={() => setShowIncome(false)} onSaved={load} />
      )}
    </RequireAuth>
  );
}
