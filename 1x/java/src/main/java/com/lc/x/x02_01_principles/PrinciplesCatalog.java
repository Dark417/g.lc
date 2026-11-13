package com.lc.x.x02_01_principles;

import com.lc.x.x02_01_principles.general.CohesionCoupling;
import com.lc.x.x02_01_principles.general.CompositionOverInheritance;
import com.lc.x.x02_01_principles.general.Cqs;
import com.lc.x.x02_01_principles.general.Dry;
import com.lc.x.x02_01_principles.general.EncapsulateWhatVaries;
import com.lc.x.x02_01_principles.general.FailFast;
import com.lc.x.x02_01_principles.general.Kiss;
import com.lc.x.x02_01_principles.general.LawOfDemeter;
import com.lc.x.x02_01_principles.general.LeastAstonishment;
import com.lc.x.x02_01_principles.general.ProgramToInterface;
import com.lc.x.x02_01_principles.general.SeparationOfConcerns;
import com.lc.x.x02_01_principles.general.TellDontAsk;
import com.lc.x.x02_01_principles.general.Yagni;
import com.lc.x.x02_01_principles.solid.Dip;
import com.lc.x.x02_01_principles.solid.Isp;
import com.lc.x.x02_01_principles.solid.Lsp;
import com.lc.x.x02_01_principles.solid.Ocp;
import com.lc.x.x02_01_principles.solid.Srp;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Supplier;

/**
 * Name -> demo for Parts A and B (plain Java, no container), in doc order.
 * - Part C demos need the container and come from SpringPrinciplesDemo.demos().
 * - Names match the Python api module so both apps answer the same URLs.
 */
public final class PrinciplesCatalog {

    private PrinciplesCatalog() {
    }

    public static Map<String, Supplier<String>> plain() {
        Map<String, Supplier<String>> m = new LinkedHashMap<>();
        // Part A — SOLID
        m.put("srp", Srp::demo);
        m.put("ocp", Ocp::demo);
        m.put("lsp", Lsp::demo);
        m.put("isp", Isp::demo);
        m.put("dip", Dip::demo);
        // Part B — general
        m.put("dry", Dry::demo);
        m.put("kiss", Kiss::demo);
        m.put("yagni", Yagni::demo);
        m.put("soc", SeparationOfConcerns::demo);
        m.put("cohesion", CohesionCoupling::demo);
        m.put("composition", CompositionOverInheritance::demo);
        m.put("interface", ProgramToInterface::demo);
        m.put("encapsulate", EncapsulateWhatVaries::demo);
        m.put("demeter", LawOfDemeter::demo);
        m.put("tell", TellDontAsk::demo);
        m.put("cqs", Cqs::demo);
        m.put("failfast", FailFast::demo);
        m.put("pola", LeastAstonishment::demo);
        return m;
    }
}
